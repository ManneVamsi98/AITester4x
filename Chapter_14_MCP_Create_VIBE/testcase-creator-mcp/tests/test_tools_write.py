"""Write-tool tests: gating, add (dry-run and real) and update."""

from __future__ import annotations

import pytest
from fastmcp.exceptions import ToolError


VALID_DRAFT = {
    "summary": "[Reports] Functional: verify scheduled email export",
    "description": (
        "As a QA engineer, verify the scheduled email export in the Reports module to make "
        "sure it behaves correctly for functional scenarios on desktop (Chrome 148)."
    ),
    "priority": "High",
    "module": "Reports",
    "test_type": "Functional",
    "preconditions": "A VWO account with access to Reports; at least one active project.",
    "steps": [
        "1. Log in to VWO and open the Reports module.",
        "2. Navigate to the scheduled email screen.",
        "3. Trigger the scheduled email export.",
        "4. Observe the result on desktop using Chrome 148.",
    ],
    "expected_result": "The scheduled email export is created and shown in the UI.",
    "browser": "Chrome 148",
    "device": "desktop",
}


def test_write_tools_present(write_tool_names):
    assert "add_test_cases" in write_tool_names
    assert "update_test_case" in write_tool_names
    assert "get_test_case_template" in write_tool_names


def test_add_dry_run_assigns_without_writing(call_write_tool):
    data = call_write_tool("add_test_cases", {"test_cases": [VALID_DRAFT], "dry_run": True}).data
    assert data["dry_run"] is True
    assert data["assigned_keys"] == ["VWO-6001"]
    assert data["would_write"] == 1

    got = call_write_tool("get_test_case", {"issue_keys": ["VWO-6001"]}).data
    assert got["missing"] == ["VWO-6001"]


def test_add_real_writes_and_retrieves(call_write_tool):
    data = call_write_tool("add_test_cases", {"test_cases": [VALID_DRAFT], "dry_run": False}).data
    assert data["dry_run"] is False
    assert data["assigned_keys"] == ["VWO-6001"]

    got = call_write_tool("get_test_case", {"issue_keys": ["VWO-6001"]}).data
    assert got["found"][0]["key"] == "VWO-6001"
    assert got["found"][0]["module"] == "Reports"
    assert got["found"][0]["status"] == "Draft"


def test_add_invalid_draft_raises(call_write_tool):
    bad = dict(VALID_DRAFT, summary="not matching the pattern")
    with pytest.raises(ToolError):
        call_write_tool("add_test_cases", {"test_cases": [bad], "dry_run": False})


def test_update_test_case(call_write_tool):
    call_write_tool("add_test_cases", {"test_cases": [VALID_DRAFT], "dry_run": False})
    data = call_write_tool(
        "update_test_case",
        {"issue_key": "VWO-6001", "changes": {"status": "Automated", "priority": "Highest"}},
    ).data
    assert data["diff"]["status"]["after"] == "Automated"
    assert data["diff"]["priority"]["after"] == "Highest"

    got = call_write_tool("get_test_case", {"issue_keys": ["VWO-6001"]}).data
    assert got["found"][0]["status"] == "Automated"


def test_update_unknown_key_raises(call_write_tool):
    with pytest.raises(ToolError):
        call_write_tool(
            "update_test_case", {"issue_key": "VWO-9999", "changes": {"status": "Automated"}}
        )


def test_multiple_adds_get_sequential_keys(call_write_tool):
    data = call_write_tool(
        "add_test_cases", {"test_cases": [VALID_DRAFT, VALID_DRAFT], "dry_run": True}
    ).data
    assert data["assigned_keys"] == ["VWO-6001", "VWO-6002"]
