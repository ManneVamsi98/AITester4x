"""Streamlit UI for the n8n "Requirement -> BDD/Gherkin Test Cases" workflow.

Enter a Jira issue key (a user story or PRD ticket) and this app calls the
workflow's webhook. The workflow fetches the story, has an AI agent draft
positive and negative Gherkin scenarios, appends one Google Sheets row per
scenario, and returns those rows -- which this app renders as a BDD feature.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import requests
import streamlit as st

ISSUE_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")

SCENARIO_TYPE_COLOR = {
    "Positive": "green",
    "Negative": "red",
    "Boundary": "orange",
    "Edge Case": "violet",
}

PRIORITY_COLOR = {"High": "red", "Medium": "orange", "Low": "gray"}

TABLE_COLUMNS = [
    ("scenario_id", "ID"),
    ("scenario_title", "Scenario"),
    ("scenario_type", "Type"),
    ("priority", "Priority"),
    ("automation_candidate", "Automation"),
]


def webhook_url(base_url: str, path: str, mode: str) -> str:
    """Build the webhook URL for the chosen mode (production or test)."""
    prefix = "webhook-test" if mode == "Test" else "webhook"
    return f"{base_url.rstrip('/')}/{prefix}/{path.strip('/')}"


def normalise_response(payload: Any) -> list[dict[str, Any]]:
    """Coerce the workflow's reply into a list of scenario rows.

    n8n returns the last node's items as a list. Older or wrapped responses may
    nest them under a single "data" key.
    """
    data = payload
    if isinstance(data, dict) and set(data.keys()) == {"data"}:
        data = data["data"]
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def call_workflow(
    url: str,
    issue_key: str,
    timeout: int,
    header_name: str | None,
    header_value: str | None,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """POST the issue key to the workflow. Returns (rows, error_message)."""
    headers = {"Content-Type": "application/json"}
    if header_name and header_value:
        headers[header_name] = header_value

    try:
        response = requests.post(
            url,
            json={"issueKey": issue_key, "requestedBy": "streamlit-ui"},
            headers=headers,
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        return None, (
            f"Timed out after {timeout}s. The agent may still be running -- check the "
            "n8n executions list; the sheet may already have been written."
        )
    except requests.exceptions.ConnectionError:
        return None, f"Could not reach n8n at {url}. Check the base URL and that the instance is up."
    except requests.exceptions.RequestException as exc:
        return None, f"Request failed: {exc}"

    if response.status_code == 404:
        return None, (
            f"404 from {url}. The webhook is not registered.\n\n"
            "- **Production mode** needs the workflow to be **Active**.\n"
            "- **Test mode** only works while the editor is listening -- open the workflow, "
            "click *Listen for test event*, then submit."
        )
    if response.status_code >= 400:
        detail = response.text.strip()[:800] or "(empty body)"
        return None, f"n8n returned HTTP {response.status_code}:\n\n{detail}"

    if not response.text.strip():
        return None, "n8n returned an empty body. Check the last node of the execution for an error."

    try:
        payload = response.json()
    except ValueError:
        return None, f"n8n returned a non-JSON response:\n\n{response.text.strip()[:800]}"

    rows = normalise_response(payload)
    if not rows:
        return None, (
            "n8n returned no scenario rows. Usually the agent failed schema validation, or the "
            "Jira key was not found. Check the execution in n8n."
        )
    return rows, None


def build_feature_file(rows: list[dict[str, Any]]) -> str:
    """Assemble the scenarios into a single Gherkin .feature file."""
    first = rows[0]
    key = str(first.get("jira_key") or "").strip()
    title = str(first.get("feature_title") or first.get("story_summary") or "Requirement").strip()

    lines: list[str] = []
    if key:
        lines.append(f"@{key} @source:jira")
    lines.append(f"Feature: {title}")
    lines.append("")

    for row in rows:
        gherkin = str(row.get("gherkin") or "").strip()
        if not gherkin:
            continue
        tags = " | ".join(
            str(row.get(field) or "").strip()
            for field in ("scenario_type", "priority")
            if row.get(field)
        )
        if tags:
            lines.append(f"  # {tags}")
        for gherkin_line in gherkin.splitlines():
            lines.append("  " + gherkin_line.rstrip())
        lines.append("")

    return "\n".join(lines)


def render_scenario(row: dict[str, Any], index: int) -> None:
    """Render one scenario as an expandable card."""
    scenario_id = str(row.get("scenario_id") or f"SC-{index:03d}")
    title = str(row.get("scenario_title") or "Untitled scenario")
    scenario_type = str(row.get("scenario_type") or "")
    priority = str(row.get("priority") or "")

    heading = f"{scenario_id} — {title}"
    with st.expander(heading, expanded=index == 1):
        badges = st.columns(2)
        with badges[0]:
            if scenario_type:
                st.markdown(f"**Type** : {SCENARIO_TYPE_COLOR.get(scenario_type, 'gray')}[{scenario_type}]")
        with badges[1]:
            if priority:
                st.markdown(f"**Priority** : {PRIORITY_COLOR.get(priority, 'gray')}[{priority}]")

        if row.get("gherkin"):
            st.code(str(row["gherkin"]).strip(), language="gherkin")

        for field, label in (
            ("preconditions", "Preconditions"),
            ("test_data", "Test data"),
            ("expected_result", "Expected result"),
            ("requirement_ref", "Traces to"),
            ("automation_candidate", "Automation"),
        ):
            value = row.get(field)
            if value not in (None, ""):
                st.markdown(f"**{label}**")
                st.markdown(str(value))
                st.write("")


def render_rows(rows: list[dict[str, Any]]) -> None:
    """Render the full set of scenarios for one requirement."""
    first = rows[0]
    feature_title = str(first.get("feature_title") or "Requirement")
    jira_key = str(first.get("jira_key") or "")

    st.subheader(feature_title)
    st.caption(f"Jira key: {jira_key} · {len(rows)} scenario(s) · source: {first.get('source_system', 'n/a')}")

    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("scenario_type") or "Unspecified")
        counts[key] = counts.get(key, 0) + 1

    metric_cols = st.columns(len(counts) + 1 if counts else 1)
    with metric_cols[0]:
        st.metric("Scenarios", len(rows))
    for i, (name, count) in enumerate(sorted(counts.items()), start=1):
        with metric_cols[i]:
            st.metric(name, count)

    review = str(first.get("review_status") or "")
    if review:
        st.warning(f"**{review}**")

    st.divider()

    table = [
        {label: row.get(field, "") for field, label in TABLE_COLUMNS}
        for row in rows
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.divider()
    for i, row in enumerate(rows, start=1):
        render_scenario(row, i)

    st.divider()
    downloads = st.columns(2)
    with downloads[0]:
        st.download_button(
            "Download JSON",
            data=json.dumps(rows, indent=2),
            file_name=f"{jira_key or 'requirement'}-test-cases.json",
            mime="application/json",
            use_container_width=True,
        )
    with downloads[1]:
        st.download_button(
            "Download .feature",
            data=build_feature_file(rows),
            file_name=f"{jira_key or 'requirement'}.feature",
            mime="text/plain",
            use_container_width=True,
        )

    with st.expander("Raw JSON"):
        st.code(json.dumps(rows, indent=2), language="json")


def main() -> None:
    st.set_page_config(page_title="Requirement to Test Cases", page_icon=None, layout="wide")

    st.title("Requirement to BDD/Gherkin Test Cases")
    st.caption(
        "Turns a Jira user story into positive and negative Gherkin scenarios. "
        "One Google Sheets row is appended per scenario."
    )

    with st.sidebar:
        st.header("n8n connection")
        base_url = st.text_input(
            "n8n base URL",
            value=os.environ.get("N8N_BASE_URL", "https://boxubum.app.n8n.cloud"),
        )
        path = st.text_input(
            "Webhook path",
            value=os.environ.get("N8N_WEBHOOK_PATH", "requirement-to-testcases"),
        )
        mode = st.radio(
            "Webhook mode",
            options=["Production", "Test"],
            index=0,
            captions=[
                "Requires the workflow to be Active.",
                "Only works while the editor is listening.",
            ],
        )
        timeout = st.number_input(
            "Timeout (seconds)",
            min_value=10,
            max_value=600,
            value=int(os.environ.get("N8N_TIMEOUT", "180")),
            step=10,
            help="Fetching the story and drafting scenarios takes a while.",
        )

        st.subheader("Optional auth header")
        st.caption("Only needed if the Webhook node has authentication enabled.")
        header_name = st.text_input("Header name", value=os.environ.get("N8N_AUTH_HEADER_NAME", ""))
        header_value = st.text_input(
            "Header value",
            value=os.environ.get("N8N_AUTH_HEADER_VALUE", ""),
            type="password",
        )

    url = webhook_url(base_url, path, mode)
    st.caption(f"POST {url}")

    issue_key = st.text_input("Jira issue key", placeholder="KAN-8").strip().upper()

    if st.button("Generate test cases", type="primary"):
        if not issue_key:
            st.error("Enter a Jira issue key.")
        elif not ISSUE_KEY_PATTERN.match(issue_key):
            st.error(f"'{issue_key}' is not a valid Jira issue key. Expected a format like KAN-8.")
        else:
            with st.spinner(f"Drafting Gherkin scenarios for {issue_key}..."):
                rows, error = call_workflow(
                    url,
                    issue_key,
                    int(timeout),
                    header_name.strip() or None,
                    header_value.strip() or None,
                )
            if error:
                st.error(error)
            elif rows:
                st.session_state["rows"] = rows
                st.session_state["key"] = issue_key
                st.success(f"Generated {len(rows)} scenario(s) for {issue_key}.")
                st.caption("The same rows were appended to your Google Sheet.")

    if st.session_state.get("rows"):
        st.divider()
        render_rows(st.session_state["rows"])


if __name__ == "__main__":
    main()
