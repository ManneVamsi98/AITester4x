"""Export and convert tools: export, Gherkin conversion, automation stubs."""

from __future__ import annotations

import csv
import io
import json
import os
from typing import Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from tc_mcp import config
from tc_mcp.models import TestCase, TestFilter
from tc_mcp.repository import Repository

ExportFormat = Literal["csv", "jira_csv", "markdown", "json"]


def _resolve_selection(
    repo: Repository,
    issue_keys: Optional[list[str]],
    filter: Optional[TestFilter],
) -> tuple[list[TestCase], list[str]]:
    if issue_keys:
        cases = []
        missing = []
        for raw in issue_keys:
            case = repo.get(raw)
            if case is None:
                missing.append(raw.strip().upper())
            else:
                cases.append(case)
        return cases, missing
    return repo.filter(filter or TestFilter()), []


def _to_csv(cases: list[TestCase]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Issue Key", "Summary", "Module", "Feature", "Priority", "Test Type", "Status", "Browser", "Device"])
    for case in cases:
        writer.writerow(
            [case.issue_key, case.summary, case.module, case.feature,
             case.priority.value, case.test_type.value, case.status.value, case.browser, case.device]
        )
    return buf.getvalue()


def _to_jira_csv(cases: list[TestCase]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Summary", "Description", "Priority", "Issue Type", "Labels"])
    for case in cases:
        writer.writerow(
            [case.summary, case.description, case.priority.value, "Test", " ".join(case.labels)]
        )
    return buf.getvalue()


def _to_markdown(cases: list[TestCase]) -> str:
    lines = ["| Key | Summary | Priority | Type | Status | Browser | Device |"]
    lines.append("|---|---|---|---|---|---|---|")
    for case in cases:
        lines.append(
            f"| {case.issue_key} | {case.summary} | {case.priority.value} | "
            f"{case.test_type.value} | {case.status.value} | {case.browser} | {case.device} |"
        )
    return "\n".join(lines)


def _to_json(cases: list[TestCase]) -> str:
    return json.dumps([c.to_full() for c in cases], indent=2)


def _format(cases: list[TestCase], fmt: ExportFormat) -> str:
    if fmt == "csv":
        return _to_csv(cases)
    if fmt == "jira_csv":
        return _to_jira_csv(cases)
    if fmt == "markdown":
        return _to_markdown(cases)
    return _to_json(cases)


def _strip_step_number(step: str) -> str:
    return step.strip().split(". ", 1)[-1] if ". " in step else step.strip()


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"export"},
        annotations={"readOnlyHint": True},
        description=(
            "Export a selection of test cases (by issue keys or filter) to csv, jira_csv, "
            "markdown or json. Up to 50 rows are returned inline; larger selections are written "
            "to a file whose path is returned."
        ),
    )
    def export_test_cases(
        issue_keys: Optional[list[str]] = None,
        filter: Optional[TestFilter] = None,
        format: ExportFormat = "csv",
    ) -> dict:
        cases, missing = _resolve_selection(repo, issue_keys, filter)
        content = _format(cases, format)

        if len(cases) <= config.MAX_EXPORT_INLINE:
            return {
                "count": len(cases),
                "format": format,
                "inline": True,
                "content": content,
                "missing_keys": missing,
            }

        os.makedirs(config.EXPORT_DIR, exist_ok=True)
        safe = {"csv": "csv", "jira_csv": "csv", "markdown": "md", "json": "json"}[format]
        path = os.path.join(config.EXPORT_DIR, f"tc_export_{len(cases)}.{safe}")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        return {
            "count": len(cases),
            "format": format,
            "inline": False,
            "path": path,
            "missing_keys": missing,
        }

    @mcp.tool(
        tags={"export"},
        annotations={"readOnlyHint": True},
        description=(
            "Convert one or more test cases to Gherkin .feature text: preconditions become "
            "Given, steps become When/And, the expected result becomes Then."
        ),
    )
    def convert_to_gherkin(issue_keys: list[str]) -> dict:
        if len(issue_keys) > 10:
            raise ToolError("At most 10 issue keys per call")
        scenarios = []
        missing = []
        for raw in issue_keys:
            case = repo.get(raw)
            if case is None:
                missing.append(raw.strip().upper())
                continue
            lines = [f"  Scenario: {case.summary}"]
            if case.preconditions:
                lines.append(f"    Given {case.preconditions}")
            for i, step in enumerate(case.steps):
                keyword = "When" if i == 0 else "And"
                lines.append(f"    {keyword} {_strip_step_number(step)}")
            lines.append(f"    Then {case.expected_result}")
            scenarios.append("\n".join(lines))

        feature_title = scenarios[0].split("\n")[0].strip().replace("Scenario: ", "") if scenarios else ""
        text = f"Feature: {feature_title}\n\n" + "\n\n".join(scenarios) if scenarios else ""
        return {"gherkin": text, "missing_keys": missing}

    @mcp.tool(
        tags={"export"},
        annotations={"readOnlyHint": True},
        description=(
            "Generate a pytest-playwright or Playwright TypeScript skeleton for one test case, "
            "with its steps embedded as comments."
        ),
    )
    def generate_automation_stub(
        issue_key: str,
        framework: Literal["pytest_playwright", "playwright_ts"] = "pytest_playwright",
    ) -> dict:
        case = repo.get(issue_key)
        if case is None:
            raise ToolError(f"Unknown issue key '{issue_key}'")

        func_name = re_slug(case.feature) + "_" + re_slug(case.test_type.value)
        step_comments = "\n".join(f"    # {step}" for step in case.steps)

        if framework == "pytest_playwright":
            code = (
                f"import pytest\nfrom playwright.sync_api import Page, expect\n\n\n"
                f"def test_{func_name}(page: Page):\n"
                f"    \"\"\"{case.summary}\"\"\"\n{step_comments}\n"
                f"    page.goto('https://app.vwo.com')\n"
                f"    # TODO: implement the steps above\n"
                f"    raise NotImplementedError\n"
            )
        else:
            code = (
                f"import {{ test, expect }} from '@playwright/test';\n\n"
                f"test('{case.summary}', async ({{ page }}) => {{\n"
                f"    // {case.summary}\n"
                + "\n".join(f"    // {step}" for step in case.steps) +
                f"\n    await page.goto('https://app.vwo.com');\n"
                f"    // TODO: implement the steps above\n"
                f"}});\n"
            )

        return {"framework": framework, "issue_key": case.issue_key, "code": code}


def re_slug(text: str) -> str:
    import re as _re

    text = text.lower().replace("/", " ").replace("&", " ")
    return _re.sub(r"[^a-z0-9]+", "_", text).strip("_")
