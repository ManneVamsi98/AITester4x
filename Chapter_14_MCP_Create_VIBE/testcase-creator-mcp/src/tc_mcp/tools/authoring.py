"""Authoring tools: template, add (write), update (write). Write tools are gated."""

from __future__ import annotations

from typing import Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from tc_mcp import config
from tc_mcp.models import Browser, Device, TestCaseChanges, TestCaseDraft, TestType
from tc_mcp.repository import Repository, increment_key
from tc_mcp.validation import draft_to_record, validate_draft


def _pick_examples(repo: Repository, module: str, feature: Optional[str], test_type: TestType) -> list[dict]:
    candidates = [
        c
        for c in repo.live()
        if c.module == module and (not feature or c.feature == feature)
    ]
    candidates = [c for c in candidates if c.test_type == test_type] or candidates
    candidates.sort(key=lambda c: c.issue_key)
    return [c.to_full() for c in candidates[:3]]


def register(mcp: FastMCP, repo: Repository, allow_write: bool) -> None:
    @mcp.tool(
        tags={"authoring"},
        annotations={"readOnlyHint": True},
        description=(
            "Return a pre-filled VWO-format skeleton plus three real examples to learn from. "
            "Use this before authoring. To save a draft, use add_test_cases."
        ),
    )
    def get_test_case_template(
        module: str,
        feature: str,
        test_type: TestType,
        browser: Browser = "Chrome 148",
        device: Device = "desktop",
    ) -> dict:
        canonical = repo.resolve_module(module)
        template = {
            "summary": f"[{canonical}] {test_type.value}: <action> {feature}",
            "description": (
                f"As a QA engineer, <action> the {feature} in the {canonical} module to make sure "
                f"it behaves correctly for {test_type.value.lower()} scenarios on {device} ({browser})."
            ),
            "priority": "Medium",
            "module": canonical,
            "test_type": test_type.value,
            "preconditions": (
                f"A VWO account with access to {canonical}; at least one active project; "
                f"{browser} on {device}."
            ),
            "steps": [
                f"1. Log in to VWO and open the {canonical} module.",
                f"2. Navigate to the {feature} screen.",
                f"3. Perform the {feature} action with valid inputs and save.",
                f"4. Observe the result on {device} using {browser}.",
            ],
            "expected_result": "<specific, measurable expected result>",
            "browser": browser,
            "device": device,
        }
        rules = {
            "summary_format": "[Module] Type: action feature",
            "steps": "exactly 4 steps, joined with ' | ' when stored",
            "allowed_priorities": config.PRIORITY_ORDER,
            "allowed_test_types": sorted(t.value for t in TestType),
            "allowed_browsers": ["Chrome 148", "Firefox 141", "Safari 19", "Edge 148"],
            "allowed_devices": ["desktop", "mobile (Android)", "mobile (iOS)", "tablet"],
            "default_status": "Draft",
        }
        return {
            "template": template,
            "examples": _pick_examples(repo, canonical, feature, test_type),
            "rules": rules,
        }

    if not allow_write:
        return

    @mcp.tool(
        tags={"authoring"},
        annotations={"readOnlyHint": False, "idempotentHint": False},
        description=(
            "Validate and add one or more new test cases. Keys are assigned from VWO-6001 up and "
            "rows are appended to the overlay (the source CSV is never changed). Defaults to "
            "dry_run=true, which returns the assigned keys and any validation errors without "
            "writing; call again with dry_run=false to actually save."
        ),
    )
    def add_test_cases(
        test_cases: list[TestCaseDraft],
        dry_run: bool = True,
    ) -> dict:
        if len(test_cases) > config.MAX_ADD:
            raise ToolError(f"At most {config.MAX_ADD} test cases can be added per call")

        records = []
        validation_results = []
        keys: list = []
        next_key = repo.next_key()
        for draft in test_cases:
            result = validate_draft(draft, repo)
            validation_results.append(result)
            if result["errors"]:
                keys.append(None)
                continue
            key = next_key
            next_key = increment_key(key)
            record = draft_to_record(draft, repo, key)
            records.append(record)
            keys.append(key)

        errors = [r["errors"] for r in validation_results if r["errors"]]
        if dry_run:
            return {
                "dry_run": True,
                "assigned_keys": keys,
                "validation": validation_results,
                "would_write": len(records),
            }
        if errors:
            raise ToolError(
                f"{len(errors)} test case(s) have validation errors; fix them first: {errors}"
            )

        written_keys = repo.add_cases(records)
        return {
            "dry_run": False,
            "assigned_keys": written_keys,
            "written": len(written_keys),
            "validation": validation_results,
        }

    @mcp.tool(
        tags={"authoring"},
        annotations={"readOnlyHint": False, "idempotentHint": False},
        description=(
            "Update an existing test case's status, priority, steps, expected result, summary, "
            "description, browser or device. Writes a new copy to the overlay (latest copy wins). "
            "The source CSV is never changed."
        ),
    )
    def update_test_case(issue_key: str, changes: TestCaseChanges) -> dict:
        try:
            before, after = repo.update_case(issue_key, changes)
        except KeyError:
            raise ToolError(f"Unknown issue key '{issue_key}'")

        diff = {}
        before_data = before.to_full()
        after_data = after.to_full()
        for field in before_data:
            if before_data[field] != after_data[field]:
                diff[field] = {"before": before_data[field], "after": after_data[field]}

        return {
            "issue_key": issue_key,
            "diff": diff,
            "before": before_data,
            "after": after_data,
        }
