"""Resources: read-only context a client can attach (@-mention)."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from tc_mcp.models import BROWSERS, DEVICES, PRIORITIES, STATUSES, TEST_TYPES
from tc_mcp.repository import Repository


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.resource("tc://schema", name="schema", description="Column definitions and allowed values.")
    def schema() -> str:
        return json.dumps(
            {
                "columns": [
                    {"name": "Issue Key", "desc": "VWO-1001..VWO-6000, unique"},
                    {"name": "Summary", "desc": "[Module] Type: action feature"},
                    {"name": "Description", "desc": "gives the feature: ... the <feature> in the <Module> module ..."},
                    {"name": "Priority", "desc": "Low < Medium < High < Highest"},
                    {"name": "Component", "desc": "the module (17 modules)"},
                    {"name": "Labels", "desc": "module-slug type-slug regression"},
                    {"name": "Test Type", "desc": "9 values"},
                    {"name": "Preconditions", "desc": "environment setup"},
                    {"name": "Steps", "desc": "exactly 4 steps, joined with ' | '"},
                    {"name": "Expected Result", "desc": "expected outcome"},
                    {"name": "Browser", "desc": "Chrome 148 / Firefox 141 / Safari 19 / Edge 148"},
                    {"name": "Device", "desc": "desktop / mobile (Android) / mobile (iOS) / tablet"},
                    {"name": "Status", "desc": "Ready / Automated / Draft / Deprecated"},
                ],
                "allowed": {
                    "priority": PRIORITIES,
                    "test_type": TEST_TYPES,
                    "browser": BROWSERS,
                    "device": DEVICES,
                    "status": STATUSES,
                },
                "summary_format": "[Module] Type: action feature",
                "steps_format": "4 steps joined with ' | '",
            },
            indent=2,
        )

    @mcp.resource("tc://modules", name="modules", description="Modules with features and counts.")
    def modules() -> str:
        return json.dumps(
            {"modules": [repo.module_info(m) for m in repo.modules]},
            indent=2,
        )

    @mcp.resource("tc://stats/summary", name="stats", description="Headline numbers.")
    def stats() -> str:
        return json.dumps(repo.stats(), indent=2)

    @mcp.resource(
        "tc://test/{issue_key}",
        name="test",
        description="One test case by issue key.",
    )
    def test(issue_key: str) -> str:
        case = repo.get(issue_key)
        if case is None:
            return json.dumps({"error": f"Unknown issue key '{issue_key}'"})
        return json.dumps(case.to_full(), indent=2)
