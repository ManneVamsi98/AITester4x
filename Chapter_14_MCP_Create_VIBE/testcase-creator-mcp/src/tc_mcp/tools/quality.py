"""Quality tools: duplicates, coverage gaps, and draft validation."""

from __future__ import annotations

from collections import defaultdict
from typing import Literal, Optional

from fastmcp import FastMCP

from tc_mcp.models import BROWSERS, DEVICES, TEST_TYPES, TestCaseDraft
from tc_mcp.ranking import score
from tc_mcp.repository import Repository
from tc_mcp.validation import validate_draft


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"quality"},
        annotations={"readOnlyHint": True},
        description=(
            "Find exact and same-scenario duplicate tests, each group with a suggested keeper. "
            "Use this to clean up a module. For coverage holes, use find_coverage_gaps."
        ),
    )
    def find_duplicate_tests(
        module: Optional[str] = None,
        mode: Literal["exact", "same_scenario"] = "exact",
    ) -> dict:
        canonical = repo.resolve_module(module) if module else None

        if mode == "exact":
            raw_groups = repo.duplicate_groups(canonical) if canonical else repo.duplicate_groups()
            groups = []
            for members in raw_groups:
                keeper = min(members, key=lambda c: c.issue_key)
                groups.append(
                    {
                        "summary": keeper.summary,
                        "duplicate_count": len(members),
                        "suggested_keeper_key": keeper.issue_key,
                        "members": [c.to_compact() for c in members],
                    }
                )
        else:
            by_scenario: dict[str, list] = defaultdict(list)
            for case in repo.live():
                if canonical and case.module != canonical:
                    continue
                by_scenario[case.scenario_id].append(case)
            groups = []
            for scenario, members in by_scenario.items():
                if len(members) < 2:
                    continue
                keeper = max(members, key=lambda c: (score(c), c.issue_key))
                groups.append(
                    {
                        "summary": scenario,
                        "variant_count": len(members),
                        "suggested_keeper_key": keeper.issue_key,
                        "members": [c.to_compact() for c in members],
                    }
                )
            groups.sort(key=lambda g: -g["variant_count"])

        return {
            "mode": mode,
            "module": canonical,
            "group_count": len(groups),
            "groups": groups,
        }

    @mcp.tool(
        tags={"quality"},
        annotations={"readOnlyHint": True},
        description=(
            "Find coverage holes: missing feature x test type combinations, features with no "
            "Highest, Security or Accessibility test, and empty browser or device cells. "
            "Use this to decide what to author next."
        ),
    )
    def find_coverage_gaps(module: Optional[str] = None) -> dict:
        modules = [repo.resolve_module(module)] if module else repo.modules

        features: set[str] = set()
        for m in modules:
            features.update(repo.features_by_module.get(m, []))

        present_types: dict[str, set[str]] = defaultdict(set)
        highest_features: set[str] = set()
        security_features: set[str] = set()
        accessibility_features: set[str] = set()
        devices_by_feature: dict[str, set[str]] = defaultdict(set)
        browsers_by_feature: dict[str, set[str]] = defaultdict(set)

        for case in repo.live():
            if case.module not in modules:
                continue
            present_types[case.feature].add(case.test_type.value)
            if case.priority.value == "Highest":
                highest_features.add(case.feature)
            if case.test_type.value == "Security":
                security_features.add(case.feature)
            if case.test_type.value == "Accessibility":
                accessibility_features.add(case.feature)
            devices_by_feature[case.feature].add(case.device)
            browsers_by_feature[case.feature].add(case.browser)

        missing_combos = []
        for feature in sorted(features):
            for test_type in TEST_TYPES:
                if test_type not in present_types[feature]:
                    missing_combos.append({"feature": feature, "missing_type": test_type})

        return {
            "modules": modules,
            "features_count": len(features),
            "missing_feature_type_count": len(missing_combos),
            "missing_feature_type": missing_combos[:100],
            "features_without_highest": sorted(features - highest_features),
            "features_without_security": sorted(features - security_features),
            "features_without_accessibility": sorted(features - accessibility_features),
            "empty_device_cells": [
                {"feature": f, "missing_devices": [d for d in DEVICES if d not in devices_by_feature[f]]}
                for f in sorted(features)
                if len(devices_by_feature[f]) < len(DEVICES)
            ],
            "empty_browser_cells": [
                {"feature": f, "missing_browsers": [b for b in BROWSERS if b not in browsers_by_feature[f]]}
                for f in sorted(features)
                if len(browsers_by_feature[f]) < len(BROWSERS)
            ],
        }

    @mcp.tool(
        tags={"quality"},
        annotations={"readOnlyHint": True},
        description=(
            "Lint a draft test case before saving it. Returns blocking errors, warnings and "
            "possible duplicates. To write it, use add_test_cases after fixing any errors."
        ),
    )
    def validate_test_case(test_case: TestCaseDraft) -> dict:
        return validate_draft(test_case, repo)
