"""Jira REST API v2 client for fetching ticket details.

Uses HTTP Basic Auth (email + API token) against the Jira Cloud REST API.
Descriptions come back as ADF (Atlassian Document Format) JSON in Cloud - we
flatten that to plain text so the LLM only sees readable requirements.
"""

import json
import re

import requests

TIMEOUT_SECONDS = 15

# ADF (Atlassian Document Format) text node types - the only ones that carry text.
_ADF_TEXT_TYPES = {"text", "codeBlock", "emoticon", "hardBreak", "mention", "inlineCard"}


class JiraError(Exception):
    """Raised when Jira can't be reached or the ticket can't be fetched."""


def normalize_base_url(raw_url: str) -> str:
    """Strip a deep Jira link down to the site base URL.

    E.g. "https://x.atlassian.net/jira/software/projects/KAN/boards/1"
    -> "https://x.atlassian.net".  Trailing slashes are removed.
    """
    url = (raw_url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # Cut everything after the first path segment.
    match = re.match(r"(https?://[^/]+)", url)
    return match.group(1).rstrip("/") if match else url.rstrip("/")


def _adf_to_text(node) -> str:
    """Recursively flatten an ADF node tree into plain text."""
    if isinstance(node, dict):
        if node.get("type") in _ADF_TEXT_TYPES:
            return node.get("text", "")
        if node.get("type") == "table":
            return "\n" + "\n".join(_adf_to_text(row) for row in node.get("content", [])) + "\n"
        return " ".join(_adf_to_text(child) for child in node.get("content", [])).strip()
    if isinstance(node, list):
        return " ".join(_adf_to_text(item) for item in node).strip()
    return str(node) if node is not None else ""


def _plain_text(description) -> str:
    """Return a plain-text version of a Jira description field.

    Handles ADF JSON (dict/list), plain strings, and None.
    """
    if description is None:
        return ""
    if isinstance(description, str):
        return description.strip()
    try:
        return _adf_to_text(description).strip()
    except Exception:
        return str(description).strip()


def _extract_acceptance_criteria(description_text: str) -> str:
    """Pull the 'Acceptance Criteria' section out of the description text, if present."""
    match = re.search(
        r"(?is)acceptance\s+criteri[ae][:\s-]*(.*?)(?=\n\s*(?:\*{1,3}\s*)?[A-Z][a-z]+(?:\s+[A-Za-z]+)?[:\s-]|\Z)",
        description_text,
    )
    if not match:
        return ""
    section = match.group(1).strip()
    # Drop markdown emphasis markers and leading list bullets for a cleaner prompt.
    section = re.sub(r"[*_`]", "", section)
    return section


def get_ticket(issue_key: str, cfg: dict) -> dict:
    """Fetch one ticket and return the fields needed for test-case generation.

    Raises JiraError with a user-friendly message on any failure.
    """
    base_url = normalize_base_url(cfg.get("jira_url", ""))
    if not base_url:
        raise JiraError("Jira URL is not configured. Add it on the Settings screen first.")
    if not cfg.get("jira_email") or not cfg.get("jira_token"):
        raise JiraError("Jira credentials are not configured. Add them on the Settings screen first.")

    url = f"{base_url}/rest/api/2/issue/{issue_key}"
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

    description_text = _plain_text(fields.get("description"))
    acceptance_criteria = _extract_acceptance_criteria(description_text)

    return {
        "key": issue_key,
        "summary": fields.get("summary", "") or "",
        "description": description_text,
        "acceptance_criteria": acceptance_criteria,
        "status": ((fields.get("status") or {}).get("name")) or "Not specified",
        "issue_type": ((fields.get("issuetype") or {}).get("name")) or "Not specified",
    }
