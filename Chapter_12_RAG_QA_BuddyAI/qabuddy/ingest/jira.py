"""JIRA tickets -> one document per ticket.

Two ingestion paths:

1. **Offline export (default, always available):** drop a JQL search response or a
   list of issues into ``data/04_jira/*.json``. The live **JIRA MCP** connection
   can be pointed at this folder once its configuration is shared.
2. **Live REST fallback:** set ``JIRA_BASE_URL``, ``JIRA_EMAIL``, ``JIRA_API_TOKEN``
   and ``JIRA_JQL`` in ``.env`` and any tickets matching the JQL are fetched on
   ingest (the same pattern used in Chapters 3 and 7).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from .base import document, iter_files, read_text

SUFFIXES = [".json", ".md"]
JIRA_FIELDS = "summary,status,assignee,priority,labels,issuetype,created,updated,description"

# Markdown ticket exports (Jira "print/export" style, one file per ticket).
_KEY = re.compile(r"\[([A-Z][A-Z0-9]+-\d+)\]")
_KEY_IN_NAME = re.compile(r"([A-Z][A-Z0-9]*)[-_](\d+)")
_FIELD = re.compile(
    r"(Status|Priority|Type|Reporter|Assignee|Resolution|Labels|Project|"
    r"Created|Updated|Components):\s*([^\t\r\n]+)"
)
_SUMMARY = re.compile(r"\[[A-Z][A-Z0-9]+-\d+\]\s*(.*?)\s*(?:Created:|Updated:|$)", re.S)
_BOILERPLATE = re.compile(r"^Back to previous view$|^Generated at .*$", re.MULTILINE)


def adf_to_text(node) -> str:
    """Flatten Atlassian Document Format (or plain text) to a readable string."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return " ".join(adf_to_text(item) for item in node)
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type")
    if node_type == "text":
        return node.get("text", "")
    if node_type == "hardBreak":
        return "\n"
    if node_type in {"paragraph", "heading"}:
        return adf_to_text(node.get("content")) + "\n"
    if node_type == "codeBlock":
        return "\n```\n" + adf_to_text(node.get("content")) + "\n```\n"
    if node_type in {"bulletList", "orderedList"}:
        return "\n".join("- " + adf_to_text(i.get("content")) for i in node.get("content", []))
    if node_type == "listItem":
        return adf_to_text(node.get("content"))
    return adf_to_text(node.get("content"))


def _issue_to_doc(issue: dict, point_prefix: str) -> dict | None:
    key = issue.get("key") or issue.get("id")
    fields = issue.get("fields", issue)
    if not key:
        return None

    description = adf_to_text(fields.get("description"))
    comments = fields.get("comment", {}).get("comments", []) if isinstance(fields.get("comment"), dict) else []

    parts = [f"JIRA {key}: {fields.get('summary', '')}", description]
    for comment in comments:
        author = comment.get("author", {}).get("displayName", "")
        body = adf_to_text(comment.get("body"))
        if body.strip():
            parts.append(f"Comment ({author}): {body}")
    text = "\n\n".join(p for p in parts if p and p.strip())
    if not text.strip():
        return None

    def name(value):
        return value.get("name") if isinstance(value, dict) else value

    return document(
        text,
        point_key=f"{point_prefix}:{key}",
        source_type="jira",
        source_file=f"jira:{key}",
        jira_key=key,
        status=name(fields.get("status")),
        assignee=name(fields.get("assignee")),
        priority=name(fields.get("priority")),
        issuetype=name(fields.get("issuetype")),
        labels=",".join(fields.get("labels", []) or []),
        created=fields.get("created"),
    )


def _issues_from_file(path: Path) -> Iterable[dict]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        return payload.get("issues", [])
    if isinstance(payload, list):
        return payload
    return []


def _key_from_name(stem: str) -> str | None:
    match = _KEY_IN_NAME.search(stem)
    return f"{match.group(1)}-{match.group(2)}" if match else None


def _markdown_ticket_doc(path: Path, folder: str) -> dict | None:
    text = read_text(path)
    if not text.strip():
        return None

    key_match = _KEY.search(text)
    key = key_match.group(1) if key_match else _key_from_name(path.stem)
    summary_match = _SUMMARY.search(text)
    fields = {m.group(1).lower(): m.group(2).strip() for m in _FIELD.finditer(text)}

    body = _BOILERPLATE.sub("", text).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    if not body:
        return None

    return document(
        body,
        point_key=f"{folder}:{path.name}",
        source_type="jira",
        source_file=path.name,
        jira_key=key,
        summary=(summary_match.group(1).strip() if summary_match else None),
        status=fields.get("status"),
        assignee=fields.get("assignee"),
        priority=fields.get("priority"),
        issuetype=fields.get("type"),
        labels=fields.get("labels"),
        created=fields.get("created"),
    )


def fetch_jql(settings, max_results: int = 200) -> list[dict]:
    """Fetch issues from a live JIRA Cloud instance using the configured JQL."""
    import requests

    if not (settings.jira_base_url and settings.jira_jql):
        return []
    issues: list[dict] = []
    start_at = 0
    auth = (settings.jira_email, settings.jira_api_token)
    url = settings.jira_base_url.rstrip("/") + "/rest/api/2/search"
    while True:
        resp = requests.get(
            url,
            params={"jql": settings.jira_jql, "fields": JIRA_FIELDS, "startAt": start_at,
                    "maxResults": max_results},
            auth=auth,
            timeout=60,
        )
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("issues", [])
        issues.extend(batch)
        if len(batch) < max_results:
            break
        start_at += len(batch)
    return issues


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    base.mkdir(parents=True, exist_ok=True)
    docs: list[dict] = []

    for path in iter_files(base, SUFFIXES):
        if path.name.lower().startswith("_readme"):
            continue
        if path.suffix.lower() == ".md":
            doc = _markdown_ticket_doc(path, folder)
            if doc:
                docs.append(doc)
            continue
        prefix = f"{folder}:{path.name}"
        for issue in _issues_from_file(path):
            doc = _issue_to_doc(issue, prefix)
            if doc:
                docs.append(doc)

    if not docs:
        try:
            live = fetch_jql(settings)
        except Exception as exc:  # network/auth problems shouldn't abort a full ingest
            print(f"  ! JIRA REST fetch failed: {exc}")
            live = []
        for issue in live:
            doc = _issue_to_doc(issue, f"{folder}:live")
            if doc:
                docs.append(doc)

    if not docs:
        print(
            "  i JIRA: no tickets found. Drop a JQL export into data/04_jira/*.json, "
            "or set JIRA_BASE_URL + JIRA_JQL in .env."
        )
    return docs
