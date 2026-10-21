"""Read-tool tests: discovery, search, planning, quality, export."""

from __future__ import annotations

import pytest


def test_list_modules(call_tool):
    data = call_tool("list_modules", {}).data
    assert data["total"] == 17
    names = [m["module"] for m in data["modules"]]
    assert "Reports" in names
    reports = next(m for m in data["modules"] if m["module"] == "Reports")
    assert reports["total"] == 333
    assert reports["live"] == 306


def test_get_filter_options(call_tool):
    data = call_tool("get_filter_options", {}).data
    assert len(data["priorities"]) == 4
    assert len(data["test_types"]) == 9
    assert len(data["browsers"]) == 4
    assert len(data["devices"]) == 4
    assert data["aliases"]["sdk"] == "SDK / Server-Side API"


def test_get_test_stats_pivot(call_tool):
    data = call_tool("get_test_stats", {"group_by": ["module", "priority"]}).data
    assert data["total_tests"] == 4585
    assert data["group_by"] == ["module", "priority"]
    assert data["groups"]


def test_get_test_case_found_and_missing(call_tool):
    data = call_tool("get_test_case", {"issue_keys": ["VWO-1001", "VWO-9999"]}).data
    assert len(data["found"]) == 1
    assert data["found"][0]["key"] == "VWO-1001"
    assert data["found"][0]["steps"]
    assert data["missing"] == ["VWO-9999"]


def test_search_test_cases_by_module(call_tool):
    data = call_tool(
        "search_test_cases",
        {"filter": {"module": "reports", "min_priority": "High"}, "limit": 100},
    ).data
    assert data["total_matched"] == 119
    assert all(r["module"] == "Reports" for r in data["results"])


def test_search_limit_clamped(call_tool):
    data = call_tool("search_test_cases", {"limit": 1000, "detail": "full"}).data
    assert data["returned"] <= 25
    assert data["note"]


def test_search_by_keyword(call_tool):
    data = call_tool("search_by_keyword", {"query": "SSO login"}).data
    assert data["total_matched"] > 0
    assert data["results"][0]["matched_fields"]


def test_get_top_tests_for_module(call_tool):
    data = call_tool(
        "get_top_tests_for_module", {"module": "reports", "count": 5, "browser": "Safari 19"}
    ).data
    assert data["returned"] == 5
    for row in data["results"]:
        assert row["module"] == "Reports"
        assert row["browser"] == "Safari 19"
        assert "rank_reason" in row
        assert "score" in row


def test_get_similar_test_cases(call_tool):
    data = call_tool("get_similar_test_cases", {"issue_key": "VWO-1001", "limit": 5}).data
    assert data["results"][0]["key"] == "VWO-1001"


def test_build_smoke_suite(call_tool):
    data = call_tool("build_test_suite", {"suite_type": "smoke", "modules": ["all"], "max_tests": 100}).data
    assert data["suite_type"] == "smoke"
    assert data["total_tests"] <= 72
    assert data["makeup"]["by_module"]


def test_build_suite_unknown_module_raises(call_tool):
    with pytest.raises(Exception):
        call_tool("build_test_suite", {"suite_type": "smoke", "modules": ["nope"]})


def test_browser_device_matrix(call_tool):
    data = call_tool("get_browser_device_matrix", {}).data
    assert set(data["browsers"]) == {"Chrome 148", "Firefox 141", "Safari 19", "Edge 148"}
    assert set(data["devices"]) == {"desktop", "mobile (Android)", "mobile (iOS)", "tablet"}


def test_automation_candidates(call_tool):
    data = call_tool("get_automation_candidates", {"module": "reports", "limit": 10}).data
    assert all(r["status"] == "Ready" for r in data["results"])
    assert all("reason" in r for r in data["results"])


def test_estimate_effort_by_keys(call_tool):
    data = call_tool("estimate_execution_effort", {"issue_keys": ["VWO-1001", "VWO-1002"]}).data
    assert data["total_tests"] == 2
    assert data["total_minutes"] >= 0


def test_find_duplicates(call_tool):
    data = call_tool("find_duplicate_tests", {"mode": "exact"}).data
    assert data["group_count"] == 439
    for group in data["groups"][:3]:
        assert group["duplicate_count"] >= 2
        assert "suggested_keeper_key" in group


def test_find_coverage_gaps(call_tool):
    data = call_tool("find_coverage_gaps", {"module": "reports"}).data
    assert data["features_count"] == 4
    assert "features_without_highest" in data


def test_validate_test_case_errors(call_tool):
    data = call_tool(
        "validate_test_case",
        {"test_case": {"summary": "no brackets", "description": "desc", "priority": "High",
                       "module": "Reports", "test_type": "Functional", "preconditions": "p",
                       "steps": ["one"], "expected_result": "works as expected"}},
    ).data
    assert data["errors"], "expected summary-pattern error"
    assert data["warnings"]


def test_get_test_case_template(call_tool):
    data = call_tool(
        "get_test_case_template",
        {"module": "reports", "feature": "scheduled email", "test_type": "Functional"},
    ).data
    assert data["template"]["module"] == "Reports"
    assert len(data["examples"]) == 3
    assert "rules" in data


def test_export_inline(call_tool):
    data = call_tool(
        "export_test_cases",
        {"issue_keys": ["VWO-1001", "VWO-1002"], "format": "markdown"},
    ).data
    assert data["inline"] is True
    assert "VWO-1001" in data["content"]


def test_convert_to_gherkin(call_tool):
    data = call_tool("convert_to_gherkin", {"issue_keys": ["VWO-1001"]}).data
    assert "Feature:" in data["gherkin"]
    assert "Scenario:" in data["gherkin"]
    assert "Given" in data["gherkin"]
    assert "Then" in data["gherkin"]


def test_generate_automation_stub(call_tool):
    data = call_tool(
        "generate_automation_stub",
        {"issue_key": "VWO-1001", "framework": "pytest_playwright"},
    ).data
    assert "def test_" in data["code"]
    assert "VWO-1001" in data["issue_key"]


def test_read_only_tools_hidden(call_tool, tool_names):
    names = tool_names
    assert "add_test_cases" not in names
    assert "update_test_case" not in names
    assert len(names) == 19
