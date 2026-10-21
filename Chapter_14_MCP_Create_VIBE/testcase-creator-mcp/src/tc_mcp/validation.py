"""Validation: turn drafts into records and lint them before saving."""

from __future__ import annotations

import re

from tc_mcp import config
from tc_mcp.models import Status, TestCase, TestCaseDraft
from tc_mcp.repository import Repository, extract_feature, module_slug

SUMMARY_PATTERN = re.compile(r"^\[[^\]]+\]\s+[^:]+:\s*.+")


def draft_to_record(draft: TestCaseDraft, repo: Repository, issue_key: str) -> TestCase:
    canonical = repo.resolver.resolve(draft.module)
    feature = extract_feature(draft.description, canonical, draft.summary)
    labels = draft.labels or [module_slug(canonical), _type_slug(draft.test_type.value), "regression"]
    return TestCase(
        issue_key=issue_key,
        summary=draft.summary,
        description=draft.description,
        priority=draft.priority,
        module=canonical,
        feature=feature,
        labels=labels,
        test_type=draft.test_type,
        preconditions=draft.preconditions,
        steps=draft.steps,
        expected_result=draft.expected_result,
        browser=draft.browser,
        device=draft.device,
        status=Status.Draft,
        scenario_id=draft.summary,
    )


def _type_slug(test_type: str) -> str:
    return test_type.lower().replace("/", "-").replace(" ", "-")


def validate_draft(draft: TestCaseDraft, repo: Repository) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not SUMMARY_PATTERN.match(draft.summary or ""):
        errors.append("Summary should match '[Module] Type: action feature'")

    if not draft.steps:
        errors.append("At least one step is required")
    elif len(draft.steps) < 3:
        warnings.append(f"Only {len(draft.steps)} step(s); the VWO standard is 4")

    normalized = (draft.expected_result or "").strip().lower().rstrip(".")
    if normalized in config.GENERIC_EXPECTED_RESULTS:
        warnings.append("Expected result looks generic; make it specific and measurable")

    possible_duplicates = repo.find_possible_duplicates(draft)

    return {
        "errors": errors,
        "warnings": warnings,
        "possible_duplicates": possible_duplicates,
    }
