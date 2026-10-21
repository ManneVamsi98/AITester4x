"""Data-layer tests: load, normalize, index, duplicates and filters."""

from __future__ import annotations

import pytest

from tc_mcp import config
from tc_mcp.models import Priority, Status, TestFilter
from tc_mcp.repository import Repository
from tc_mcp.resolver import ModuleResolver


def test_loads_all_rows(repo: Repository):
    assert len(repo.cases) == 5000
    assert len(repo.modules) == 17
    assert sum(len(v) for v in repo.features_by_module.values()) == 72


def test_live_and_deprecated_counts(repo: Repository):
    live = repo.live()
    assert len(live) == 4585
    deprecated = sum(1 for c in repo.cases if c.status == Status.Deprecated)
    assert deprecated == 415


def test_priority_breakdown(repo: Repository):
    counts = {"Highest": 0, "High": 0, "Medium": 0, "Low": 0}
    for c in repo.cases:
        counts[c.priority.value] += 1
    assert counts == {"Highest": 396, "High": 1546, "Medium": 2198, "Low": 860}


def test_duplicate_count(repo: Repository):
    assert len(repo._duplicate_keys) == 466


def test_scenario_count(repo: Repository):
    scenarios = {c.scenario_id for c in repo.cases}
    assert len(scenarios) == 1520


def test_no_broken_a_label(repo: Repository):
    ab = [c for c in repo.cases if c.module == "A/B Testing"]
    assert ab, "expected A/B Testing rows"
    for c in ab:
        assert "a" not in c.labels, f"broken 'a' label found: {c.labels}"
        assert c.labels[0] == "ab-testing"


def test_no_doubled_regression_label(repo: Repository):
    for c in repo.cases:
        if c.test_type.value == "Regression":
            assert c.labels.count("regression") == 1, f"doubled label: {c.labels}"


def test_feature_extraction(repo: Repository):
    reports = [c for c in repo.cases if c.module == "Reports"]
    features = {c.feature for c in reports}
    assert "scheduled email" in features
    assert "report export" in features


def test_resolver_aliases(repo: Repository):
    assert repo.resolver.resolve("ab testing") == "A/B Testing"
    assert repo.resolver.resolve("sdk") == "SDK / Server-Side API"
    assert repo.resolver.resolve("billing") == "Account & Billing"
    assert repo.resolver.resolve("REPORTS") == "Reports"


def test_resolver_unknown_module(repo: Repository):
    from fastmcp.exceptions import ToolError

    with pytest.raises(ToolError):
        repo.resolver.resolve("does not exist")


def test_filter_by_module_and_priority(repo: Repository):
    f = TestFilter(module="reports", min_priority=Priority.High)
    result = repo.filter(f)
    assert result
    assert all(c.module == "Reports" for c in result)
    assert all(c.priority in (Priority.High, Priority.Highest) for c in result)


def test_filter_excludes_deprecated_by_default(repo: Repository):
    f = TestFilter()
    result = repo.filter(f)
    assert len(result) == 4585
    assert all(c.status != Status.Deprecated for c in result)


def test_filter_include_duplicates(repo: Repository):
    with_dupes = repo.filter(TestFilter(include_duplicates=True))
    without_dupes = repo.filter(TestFilter(include_duplicates=False))
    assert len(with_dupes) == 4585
    live_duplicate_keys = {k for k in repo._duplicate_keys if repo.by_key[k].live}
    assert len(without_dupes) == len(with_dupes) - len(live_duplicate_keys)


def test_filter_min_max_priority(repo: Repository):
    low = repo.filter(TestFilter(max_priority=Priority.Low))
    assert all(c.priority == Priority.Low for c in low)


def test_next_key(repo: Repository):
    assert repo.next_key() == "VWO-6001"
