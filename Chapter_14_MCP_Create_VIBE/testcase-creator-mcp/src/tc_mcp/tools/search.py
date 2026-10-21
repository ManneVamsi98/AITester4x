"""Find and fetch tools: get_test_case, search, keyword, top tests, similar tests."""

from __future__ import annotations

from typing import Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from tc_mcp import config
from tc_mcp.models import Browser, Device, Priority, TestCase, TestFilter, TestType
from tc_mcp.ranking import top_cases
from tc_mcp.repository import Repository
from tc_mcp.tools.common import (
    clamp_limit,
    compact_rows,
    detail_rows,
    envelope,
    full_rows,
    paginate,
    sort_cases,
)


def _filter_summary(f: TestFilter) -> dict:
    data = f.model_dump(exclude_none=True, exclude_defaults=True)
    for key in ("priority", "test_type", "status", "min_priority", "max_priority"):
        if key in data and data[key] is not None:
            if isinstance(data[key], list):
                data[key] = [v.value if hasattr(v, "value") else v for v in data[key]]
            elif hasattr(data[key], "value"):
                data[key] = data[key].value
    if "module" in data and f.modules is None and isinstance(data.get("module"), str):
        # resolved module stored separately is not needed here; keep raw input.
        pass
    return data


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"search"},
        annotations={"readOnlyHint": True},
        description=(
            "Fetch the full detail of one or more test cases by their VWO issue key "
            "(e.g. VWO-1004). Unknown keys are reported separately. For filtering instead of "
            "key lookup, use search_test_cases."
        ),
    )
    def get_test_case(issue_keys: list[str]) -> dict:
        found = []
        missing = []
        for raw in issue_keys[: config.MAX_GET_KEYS]:
            key = raw.strip().upper()
            case = repo.get(key)
            if case is None:
                missing.append(key)
            else:
                found.append(case.to_full())
        return {
            "found": found,
            "missing": missing,
        }

    @mcp.tool(
        tags={"search"},
        annotations={"readOnlyHint": True},
        description=(
            "The main filter tool: find test cases by module, priority (or min/max priority "
            "range), test type, browser, device and status. Returns a paginated list envelope. "
            "For 'what should I run first' ranked advice, use get_top_tests_for_module."
        ),
    )
    def search_test_cases(
        filter: Optional[TestFilter] = None,
        sort_by: Literal["priority", "key"] = "priority",
        limit: int = config.DEFAULT_LIMIT,
        offset: int = 0,
        detail: Literal["compact", "full"] = "compact",
    ) -> dict:
        f = filter or TestFilter()
        maximum = config.MAX_FULL if detail == "full" else config.MAX_COMPACT
        limit, note = clamp_limit(limit, maximum)

        matches = repo.filter(f)
        matches = sort_cases(matches, sort_by)
        page = paginate(matches, offset, limit)

        rows = detail_rows(page, detail)
        return envelope(
            total_matched=len(matches),
            results=rows,
            offset=offset,
            limit=limit,
            filters_applied=_filter_summary(f),
            note=note,
        )

    @mcp.tool(
        tags={"search"},
        annotations={"readOnlyHint": True},
        description=(
            "Free-text search across summaries, features, descriptions, steps and expected "
            "results (e.g. 'rate limiting', 'SSO', 'invoice'). Returns ranked compact rows with "
            "the field(s) that matched. For structured filters use search_test_cases."
        ),
    )
    def search_by_keyword(query: str, module: Optional[str] = None, limit: int = 20) -> dict:
        limit, note = clamp_limit(limit, config.MAX_COMPACT)
        needle = query.strip().lower()
        canonical_module = repo.resolve_module(module) if module else None

        scored: list[tuple[TestCase, int, list[str]]] = []
        for case in repo.live():
            if canonical_module and case.module != canonical_module:
                continue
            matched: list[str] = []
            score = 0
            if needle in case.summary.lower():
                score += 5
                matched.append("summary")
            if needle in case.feature.lower():
                score += 3
                matched.append("feature")
            if needle in case.description.lower():
                score += 2
                matched.append("description")
            if needle in case.expected_result.lower():
                score += 2
                matched.append("expected_result")
            if any(needle in s.lower() for s in case.steps):
                score += 1
                matched.append("steps")
            if score:
                scored.append((case, score, matched))

        scored.sort(key=lambda item: (-item[1], item[0].issue_key))
        rows = []
        for case, score, matched in scored[:limit]:
            row = case.to_compact()
            row["score"] = score
            row["matched_fields"] = matched
            rows.append(row)

        return envelope(
            total_matched=len(scored),
            results=rows,
            offset=0,
            limit=limit,
            filters_applied={"query": query, "module": canonical_module},
            note=note,
        )

    @mcp.tool(
        tags={"search"},
        annotations={"readOnlyHint": True},
        description=(
            "Rank the test cases to run first for a module. Each result has a score and a "
            "rank_reason explaining the pick, spread across features. Use this to answer "
            "'what should I run first for X'. To list without ranking, use search_test_cases."
        ),
    )
    def get_top_tests_for_module(
        module: str,
        count: int = 10,
        test_types: Optional[list[TestType]] = None,
        browser: Optional[Browser] = None,
        device: Optional[Device] = None,
        unique_scenarios: bool = True,
    ) -> dict:
        count = max(1, min(count, 50))
        canonical = repo.resolve_module(module)

        candidates = [
            c
            for c in repo.live()
            if c.module == canonical
            and c.status.value != "Draft"
            and (not test_types or c.test_type in test_types)
            and (not browser or c.browser == browser)
            and (not device or c.device == device)
        ]

        picks = top_cases(candidates, count, unique_scenarios=unique_scenarios)
        rows = []
        for case, sc, reason in picks:
            row = case.to_compact()
            row["score"] = sc
            row["rank_reason"] = reason
            rows.append(row)

        return envelope(
            total_matched=len(candidates),
            results=rows,
            offset=0,
            limit=count,
            filters_applied={
                "module": canonical,
                "test_types": [t.value for t in test_types] if test_types else None,
                "browser": browser,
                "device": device,
                "unique_scenarios": unique_scenarios,
            },
        )

    @mcp.tool(
        tags={"search"},
        annotations={"readOnlyHint": True},
        description=(
            "Given one test case key, find the same feature tested under a different type, "
            "browser or device. Useful for review and for few-shot examples. The caller's test "
            "is returned first, then its nearest neighbours."
        ),
    )
    def get_similar_test_cases(issue_key: str, limit: int = 10) -> dict:
        limit = max(1, min(limit, 100))
        case = repo.get(issue_key)
        if case is None:
            raise ToolError(f"Unknown issue key '{issue_key}'")

        others = [
            c
            for c in repo.live()
            if c.issue_key != case.issue_key and c.feature == case.feature
        ]
        others.sort(key=lambda c: c.issue_key)

        rows = [case.to_compact()]
        for c in others[:limit]:
            differs = []
            if c.test_type != case.test_type:
                differs.append(f"type: {c.test_type.value}")
            if c.browser != case.browser:
                differs.append(f"browser: {c.browser}")
            if c.device != case.device:
                differs.append(f"device: {c.device}")
            row = c.to_compact()
            row["differs_in"] = differs
            rows.append(row)

        return envelope(
            total_matched=len(others),
            results=rows,
            offset=0,
            limit=limit,
            filters_applied={"issue_key": case.issue_key, "feature": case.feature},
        )
