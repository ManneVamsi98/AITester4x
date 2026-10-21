"""Discovery tools: learn the catalog (list_modules, get_filter_options, get_test_stats)."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Literal, Optional

from fastmcp import FastMCP

from tc_mcp.models import (
    BROWSERS,
    DEVICES,
    PRIORITIES,
    STATUSES,
    TEST_TYPES,
    TestFilter,
)
from tc_mcp.repository import Repository
from tc_mcp.tools.common import envelope

STATS_DIMENSIONS = Literal[
    "module", "priority", "test_type", "status", "browser", "device", "feature"
]


def _val(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"discovery"},
        annotations={"readOnlyHint": True},
        description=(
            "List all modules with test counts and features. Use this first to learn what "
            "modules exist and their size. For the allowed filter values, use get_filter_options."
        ),
    )
    def list_modules(include_features: bool = True) -> dict:
        modules = [repo.module_info(m) for m in repo.modules]
        if not include_features:
            for info in modules:
                info.pop("features", None)
        return {
            "total": len(modules),
            "modules": modules,
        }

    @mcp.tool(
        tags={"discovery"},
        annotations={"readOnlyHint": True},
        description=(
            "Return the exact allowed values for every filter (priority, type, browser, device, "
            "status) plus the module list and module aliases. Use this to avoid guessing enum "
            "values in search_test_cases or build_test_suite."
        ),
    )
    def get_filter_options() -> dict:
        return {
            "priorities": PRIORITIES,
            "test_types": TEST_TYPES,
            "browsers": BROWSERS,
            "devices": DEVICES,
            "statuses": STATUSES,
            "modules": repo.modules,
            "aliases": repo.resolver.alias_map(),
        }

    @mcp.tool(
        tags={"discovery"},
        annotations={"readOnlyHint": True},
        description=(
            "Pivot test counts grouped by one or two dimensions (e.g. module x priority). "
            "Use this for coverage questions like 'how many Security tests per module'. "
            "To fetch the actual test rows, use search_test_cases."
        ),
    )
    def get_test_stats(
        group_by: list[STATS_DIMENSIONS],
        filter: Optional[TestFilter] = None,
    ) -> dict:
        if not group_by:
            group_by = ["module"]
        if len(group_by) > 2:
            group_by = group_by[:2]

        cases = repo.filter(filter or TestFilter())

        def key_of(case):
            return tuple(getattr(case, dim) if dim != "feature" else case.feature for dim in group_by)

        counts: dict = Counter()
        for case in cases:
            counts[key_of(case)] += 1

        if len(group_by) == 1:
            dim = group_by[0]
            rows = [
                {"group": _val(key[0]), "count": count}
                for key, count in sorted(counts.items(), key=lambda kv: -kv[1])
            ]
        else:
            rows = [
                {"group": [_val(k) for k in key], "count": count}
                for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))
            ]

        return {
            "group_by": group_by,
            "total_tests": len(cases),
            "groups": rows,
        }
