"""Jira REST API v3 client for the Test Plan Agent.

Fetches a ticket and normalizes it: ADF description -> Markdown, acceptance
criteria resolved from the description or custom fields. Output is the
'normalized payload' consumed by the readiness gate and the LLM.
"""

import json
import re

import requests

TIMEOUT_SECONDS = 15


class JiraError(Exception):
    """Raised when Jira can't be reached or the ticket can't be fetched."""


def normalize_base_url(raw_url: str) -> str:
    """Strip a deep Jira link down to the site base URL."""
    url = (raw_url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    match = re.match(r"(https?://[^/]+)", url)
    return match.group(1).rstrip("/") if match else url.rstrip("/")


# --- ADF -> Markdown -------------------------------------------------------
def adf_to_md(node) -> str:
    """Convert an ADF node tree to Markdown."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "\n".join(adf_to_md(item) for item in node if adf_to_md(item).strip())
    if not isinstance(node, dict):
        return ""
    t = node.get("type")
    content = node.get("content") or []
    inner = " ".join(adf_to_md(c) for c in content).strip()
    text = (node.get("text") or "").strip()
    if t == "text":
        if any(m.get("type") == "code" for m in node.get("marks") or []):
            return f"`{text}`"
        if any(m.get("type") == "strong" for m in node.get("marks") or []):
            return f"**{text}**"
        if any(m.get("type") == "em" for m in node.get("marks") or []):
            return f"*{text}*"
        return text
    if t == "hardBreak":
        return "\n"
    if t == "paragraph":
        return f"{inner}\n"
    if t == "bulletList":
        return "\n".join(f"- {adf_to_md(c)}" for c in content).strip()
    if t == "orderedList":
        return "\n".join(f"{i + 1}. {adf_to_md(c)}" for i, c in enumerate(content)).strip()
    if t == "listItem":
        return adf_to_md(content).strip()
    if t == "codeBlock":
        return f"\n```\n{text or inner}\n```\n"
    if t == "heading":
        lvl = min((node.get("attrs") or {}).get("level", 2), 6)
        return f"\n{'#' * lvl} {inner}\n"
    if t == "table":
        rows = [adf_to_md(r) for r in content]
        return "\n".join(rows)
    if t in ("tableRow",):
        cells = [adf_to_md(c).strip() for c in content]
        return "| " + " | ".join(cells) + " |"
    if t in ("tableHeader", "tableCell"):
        return adf_to_md(content).strip()
    if t == "rule":
        return "\n---\n"
    if t in ("blockquote", "panel"):
        return "\n".join(f"> {line}" for line in inner.splitlines())
    return inner


def plain_md(description) -> str:
    """Return Markdown for a Jira description (ADF JSON, string, or None)."""
    if description is None:
        return ""
    if isinstance(description, str):
        return description.strip()
    try:
        return adf_to_md(description).strip()
    except Exception:
        return str(description).strip()


def _extract_acceptance_criteria(description_md: str) -> str:
    """Pull an 'Acceptance Criteria' section out of the description Markdown."""
    match = re.search(
        r"(?is)acceptance\s+criteri[ae][:\s-]*(.*?)(?=\n\s*(?:#+\s*)?[A-Z][A-Za-z]+(?:\s+[A-Za-z]+)?[:\s-]|\Z)",
        description_md,
    )
    if not match:
        return ""
    section = match.group(1).strip()
    section = re.sub(r"[*_`]", "", section)
    return section


def list_issues(cfg: dict, project: str = "KAN", max_results: int = 10) -> list:
    """List recent issues for a project (key + summary) for the UI picker."""
    base_url = normalize_base_url(cfg.get("jira_url", ""))
    if not base_url or not cfg.get("jira_email") or not cfg.get("jira_token"):
        return []
    import urllib.parse
    jql = urllib.parse.quote(f"project={project} order by created DESC")
    url = f"{base_url}/rest/api/3/search/jql?jql={jql}&fields=summary,status,issuetype,priority&maxResults={max_results}"
    auth = (cfg["jira_email"], cfg["jira_token"])
    try:
        resp = requests.get(url, auth=auth, headers={"Accept": "application/json"}, timeout=TIMEOUT_SECONDS)
        if resp.status_code != 200:
            return []
        return [
            {
                "key": i["key"],
                "summary": (i.get("fields") or {}).get("summary", ""),
                "status": ((i.get("fields") or {}).get("status") or {}).get("name", ""),
                "issue_type": ((i.get("fields") or {}).get("issuetype") or {}).get("name", ""),
            }
            for i in resp.json().get("issues", [])
        ]
    except requests.RequestException:
        return []


def fetch_ticket(issue_key: str, cfg: dict) -> dict:
    """Fetch one ticket and return the normalized payload for the plan agent.

    Raises JiraError with a user-friendly message on any failure.
    """
    base_url = normalize_base_url(cfg.get("jira_url", ""))
    if not base_url:
        raise JiraError("Jira URL is not configured. Add it on the Settings screen first.")
    if not cfg.get("jira_email") or not cfg.get("jira_token"):
        raise JiraError("Jira credentials are not configured. Add them on the Settings screen first.")

    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    auth = (cfg["jira_email"], cfg["jira_token"])
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, auth=auth, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise JiraError(f"Could not reach Jira at {base_url}: {exc}") from exc

    if resp.status_code == 401:
        raise JiraError("Jira rejected the credentials (401). Check email/token on the Settings screen.")
    if resp.status_code == 404:
        raise JiraError(f"Ticket {issue_key} was not found on this Jira site (404).")
    if resp.status_code >= 400:
        raise JiraError(f"Jira returned HTTP {resp.status_code} for {issue_key}.")

    data = resp.json()
    fields = data.get("fields", {})
    description_md = plain_md(fields.get("description"))

    # Acceptance criteria: explicit custom field, else from description section.
    acceptance_criteria = ""
    for key in ("acceptanceCriteria", "Acceptance Criteria"):
        if key in fields:
            acceptance_criteria = plain_md(fields[key])
            break
    if not acceptance_criteria:
        acceptance_criteria = _extract_acceptance_criteria(description_md)

    self_link = data.get("self", "")
    base = self_link.split("/rest/api/")[0] if self_link.startswith("http") else base_url

    return {
        "key": issue_key,
        "url": f"{base}/browse/{issue_key}",
        "summary": (fields.get("summary") or "").strip(),
        "description": description_md,
        "acceptance_criteria": acceptance_criteria.strip(),
        "status": ((fields.get("status") or {}).get("name")) or "Not specified",
        "issue_type": ((fields.get("issuetype") or {}).get("name")) or "Not specified",
        "priority": ((fields.get("priority") or {}).get("name")) or "Not specified",
        "labels": fields.get("labels") or [],
        "components": [c.get("name") for c in (fields.get("components") or []) if c.get("name")],
        "assignee": ((fields.get("assignee") or {}).get("displayName")) or "Unassigned",
        "created": (fields.get("created") or ""),
        "updated": (fields.get("updated") or ""),
    }
