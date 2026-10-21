"""Execution planning tools: suite builder, matrix, automation candidates, effort."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from tc_mcp import config
from tc_mcp.models import BROWSERS, DEVICES, Priority, TestCase, TestFilter
from tc_mcp.ranking import score, top_cases
from tc_mcp.repository import Repository
from tc_mcp.tools.common import clamp_limit, envelope

SuiteType = Literal["smoke", "sanity", "regression"]


def _estimate(cases: list[TestCase], minutes_manual: int, minutes_automated: int) -> dict:
    manual = [c for c in cases if c.status.value != "Automated"]
    automated = [c for c in cases if c.status.value == "Automated"]
    manual_minutes = len(manual) * minutes_manual
    automated_minutes = len(automated) * minutes_automated
    return {
        "total_tests": len(cases),
        "manual_tests": len(manual),
        "automated_tests": len(automated),
        "manual_minutes": manual_minutes,
        "automated_minutes": automated_minutes,
        "total_minutes": manual_minutes + automated_minutes,
    }


def _makeup(cases: list[TestCase]) -> dict:
    return {
        "by_module": dict(Counter(c.module for c in cases)),
        "by_type": dict(Counter(c.test_type.value for c in cases)),
        "by_priority": dict(Counter(c.priority.value for c in cases)),
    }


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"planning"},
        annotations={"readOnlyHint": True},
        description=(
            "Build a ready-to-run smoke, sanity or regression suite across one or many modules. "
            "Returns an ordered suite, its makeup, an effort estimate and any relaxations. "
            "To rank a single module's top tests, use get_top_tests_for_module."
        ),
    )
    def build_test_suite(
        suite_type: SuiteType,
        modules: Optional[list[str]] = None,
        min_tests: int = 1,
        max_tests: int = 50,
        browsers: Optional[list[str]] = None,
        devices: Optional[list[str]] = None,
        include_drafts: bool = False,
    ) -> dict:
        rule = config.SUITE_RULES[suite_type]
        if modules in (None, [], ["all"]):
            module_names = repo.modules
        else:
            module_names = repo.resolver.resolve_many(modules)

        priority_tiers = list(rule["priorities"]) if rule["priorities"] else None

        def select(tiers: Optional[list[str]]) -> list[tuple[TestCase, int]]:
            candidates = [
                c
                for c in repo.cases
                if c.module in module_names and c.live and (include_drafts or c.status.value != "Draft")
            ]
            if tiers is not None:
                candidates = [c for c in candidates if c.priority.value in tiers]
            if rule["types"]:
                candidates = [c for c in candidates if c.test_type.value in rule["types"]]
            if browsers:
                candidates = [c for c in candidates if c.browser in browsers]
            elif rule["browser"]:
                candidates = [c for c in candidates if c.browser == rule["browser"]]
            if devices:
                candidates = [c for c in candidates if c.device in devices]

            per_feature = rule["per_feature"]
            by_feature: dict[str, list[TestCase]] = defaultdict(list)
            for c in candidates:
                by_feature[c.feature].append(c)

            picks: list[tuple[TestCase, int]] = []
            for feature, cases in by_feature.items():
                limit = per_feature if per_feature else len(cases)
                for case, sc, _ in top_cases(cases, limit, unique_scenarios=False):
                    picks.append((case, sc))
            picks.sort(key=lambda item: (-item[1], item[0].issue_key))
            return picks

        relaxations: list[str] = []
        selected = select(priority_tiers)
        all_tiers = ["Highest", "High", "Medium", "Low"]
        if priority_tiers is not None:
            while len(selected) < min_tests:
                lowest = priority_tiers[-1]
                idx = all_tiers.index(lowest)
                if idx + 1 >= len(all_tiers):
                    break
                priority_tiers.append(all_tiers[idx + 1])
                relaxations.append(
                    f"added priority tier '{all_tiers[idx + 1]}' to reach min_tests={min_tests}"
                )
                selected = select(priority_tiers)

        if len(selected) > max_tests:
            selected = selected[: max_tests]

        cases = [case for case, _ in selected]
        rows = []
        for case, sc in selected:
            row = case.to_compact()
            row["score"] = sc
            rows.append(row)

        return {
            "suite_type": suite_type,
            "modules": module_names,
            "total_tests": len(cases),
            "makeup": _makeup(cases),
            "effort_estimate": _estimate(cases, 10, 1),
            "relaxations": relaxations,
            "tests": rows,
        }

    @mcp.tool(
        tags={"planning"},
        annotations={"readOnlyHint": True},
        description=(
            "Return a browser x device coverage grid (4x4) with test counts and empty cells "
            "flagged. Optional module or feature filter. Use it to spot where coverage is thin."
        ),
    )
    def get_browser_device_matrix(
        module: Optional[str] = None,
        feature: Optional[str] = None,
    ) -> dict:
        canonical = repo.resolve_module(module) if module else None
        cases = [
            c
            for c in repo.live()
            if (canonical is None or c.module == canonical)
            and (not feature or feature.lower() in c.feature.lower())
        ]
        grid: dict[str, dict[str, int]] = {b: {} for b in BROWSERS}
        empty_cells = []
        for browser in BROWSERS:
            for device in DEVICES:
                count = sum(1 for c in cases if c.browser == browser and c.device == device)
                grid[browser][device] = count
                if count == 0:
                    empty_cells.append({"browser": browser, "device": device})

        return {
            "module": canonical,
            "feature": feature,
            "total_tests": len(cases),
            "browsers": BROWSERS,
            "devices": DEVICES,
            "grid": grid,
            "empty_cells": empty_cells,
        }

    @mcp.tool(
        tags={"planning"},
        annotations={"readOnlyHint": True},
        description=(
            "Find Ready tests that are not yet Automated and are worth automating, ranked with a "
            "reason. To estimate how long a selection takes, use estimate_execution_effort."
        ),
    )
    def get_automation_candidates(
        module: Optional[str] = None,
        min_priority: Priority = Priority.High,
        limit: int = 20,
    ) -> dict:
        limit, note = clamp_limit(limit, config.MAX_COMPACT)
        canonical = repo.resolve_module(module) if module else None
        min_idx = config.PRIORITY_ORDER.index(min_priority.value)

        ready = [
            c
            for c in repo.cases
            if c.status.value == "Ready"
            and (canonical is None or c.module == canonical)
            and config.PRIORITY_ORDER.index(c.priority.value) >= min_idx
        ]
        variant_counts = Counter(
            c.scenario_id for c in repo.cases if c.status.value in {"Ready", "Automated"}
        )

        def rank_key(c: TestCase):
            return (
                -config.PRIORITY_ORDER.index(c.priority.value),
                -variant_counts.get(c.scenario_id, 1),
                c.issue_key,
            )

        ready.sort(key=rank_key)
        rows = []
        for case in ready[:limit]:
            row = case.to_compact()
            row["reason"] = (
                f"{case.priority.value} priority {case.test_type.value} test, "
                f"{variant_counts.get(case.scenario_id, 1)} browser/device variant(s), stable steps"
            )
            rows.append(row)

        return envelope(
            total_matched=len(ready),
            results=rows,
            offset=0,
            limit=limit,
            filters_applied={"module": canonical, "min_priority": min_priority.value},
            note=note,
        )

    @mcp.tool(
        tags={"planning"},
        annotations={"readOnlyHint": True},
        description=(
            "Estimate execution effort in minutes for a selection of tests, either by issue keys "
            "or by a filter. Splits manual vs automated. Use after build_test_suite."
        ),
    )
    def estimate_execution_effort(
        issue_keys: Optional[list[str]] = None,
        filter: Optional[TestFilter] = None,
        minutes_manual: int = 10,
        minutes_automated: int = 1,
    ) -> dict:
        if issue_keys:
            cases = []
            missing = []
            for raw in issue_keys:
                case = repo.get(raw)
                if case is None:
                    missing.append(raw.strip().upper())
                else:
                    cases.append(case)
        else:
            cases = repo.filter(filter or TestFilter())
            missing = []

        result = _estimate(cases, minutes_manual, minutes_automated)
        per_module = {}
        for case in cases:
            info = per_module.setdefault(case.module, _estimate([], minutes_manual, minutes_automated))
            info["total_tests"] += 1
            if case.status.value == "Automated":
                info["automated_tests"] += 1
                info["automated_minutes"] += minutes_automated
            else:
                info["manual_tests"] += 1
                info["manual_minutes"] += minutes_manual
            info["total_minutes"] = info["manual_minutes"] + info["automated_minutes"]

        result["by_module"] = per_module
        if missing:
            result["missing_keys"] = missing
        return result
