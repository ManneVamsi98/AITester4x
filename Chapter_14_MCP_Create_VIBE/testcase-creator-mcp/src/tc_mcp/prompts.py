"""Prompts: reusable workflows a user picks from the client menu."""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.prompt(
        description="Generate new test cases: template -> validate -> show -> save."
    )
    def generate_test_cases(module: str, feature: str, test_type: str, count: int = 3) -> str:
        return (
            f"You are authoring {count} new '{test_type}' test case(s) for the feature "
            f"'{feature}' in the '{module}' module.\n\n"
            "Work through these steps:\n"
            "1. Call get_test_case_template for the module, feature and type to get a skeleton "
            "and three real examples.\n"
            "2. Write the draft(s) in the same VWO format.\n"
            "3. Call validate_test_case on each draft and fix every error.\n"
            "4. Call add_test_cases with dry_run=true and show the user the assigned keys.\n"
            "5. After the user confirms, call add_test_cases again with dry_run=false to save.\n"
            "Never save without showing the dry-run result first."
        )

    @mcp.prompt(
        description="Plan a release run: build a suite, estimate effort, trim to fit, export."
    )
    def plan_release_run(modules: str, max_tests: int = 50, deadline_hours: int = 4) -> str:
        return (
            f"Plan the release run for module(s): {modules}.\n\n"
            "1. Call get_top_tests_for_module for each module to see what matters most.\n"
            "2. Call build_test_suite with the modules and max_tests to build a ready-to-run suite.\n"
            "3. Call estimate_execution_effort on the suite to see if it fits the deadline.\n"
            "4. If it is over budget, raise min_priority or lower max_tests and rebuild.\n"
            "5. Call export_test_cases to hand the final selection to the team.\n"
            f"Target: a suite that runs within {deadline_hours} hours."
        )

    @mcp.prompt(
        description="Review a module's coverage and report gaps and duplicates."
    )
    def review_module_coverage(module: str) -> str:
        return (
            f"Review the coverage of the '{module}' module and write a short report.\n\n"
            "1. Call get_test_stats grouped by test_type and priority for the module.\n"
            "2. Call find_coverage_gaps for the module.\n"
            "3. Call find_duplicate_tests for the module.\n"
            "4. Summarize: which test types are thin, which features lack Highest/Security/"
            "Accessibility tests, and how many duplicates should be cleaned up."
        )
