"""Ranking: score test cases and spread picks across features for "top N" results."""

from __future__ import annotations

from typing import Iterable, Optional

from tc_mcp import config
from tc_mcp.models import TestCase


def score(case: TestCase) -> int:
    return (
        config.PRIORITY_WEIGHTS.get(case.priority.value, 0)
        + config.STATUS_WEIGHTS.get(case.status.value, 0)
        + config.TYPE_WEIGHTS.get(case.test_type.value, 0)
    )


def _key_sort(case: TestCase) -> str:
    return case.issue_key


def _rank_reason(case: TestCase, position: str) -> str:
    return (
        f"{case.priority.value} | {case.status.value} | {case.test_type.value}"
        f" | {position} for feature '{case.feature or 'unknown'}'"
    )


def _sort_scored(scored: list[tuple[TestCase, int]]) -> list[tuple[TestCase, int]]:
    return sorted(scored, key=lambda item: (-item[1], _key_sort(item[0])))


def top_cases(
    cases: Iterable[TestCase],
    count: int,
    unique_scenarios: bool = True,
) -> list[tuple[TestCase, int, str]]:
    """Return up to `count` (case, score, reason) tuples, diversified across features."""
    scored = [(case, score(case)) for case in cases]
    scored = _sort_scored(scored)

    if unique_scenarios:
        best_per_scenario: dict[str, tuple[TestCase, int]] = {}
        for case, sc in scored:
            if case.scenario_id not in best_per_scenario:
                best_per_scenario[case.scenario_id] = (case, sc)
        scored = _sort_scored(list(best_per_scenario.values()))

    if not scored:
        return []

    # Round-robin across features so the top N covers several features.
    by_feature: dict[str, list[tuple[TestCase, int]]] = {}
    for case, sc in scored:
        by_feature.setdefault(case.feature, []).append((case, sc))

    feature_order = sorted(
        by_feature.keys(),
        key=lambda f: (-max(sc for _, sc in by_feature[f]), f),
    )

    picks: list[tuple[TestCase, int]] = []
    depth = 0
    while len(picks) < count:
        progressed = False
        for feature in feature_order:
            bucket = by_feature.get(feature)
            if not bucket or depth >= len(bucket):
                continue
            picks.append(bucket[depth])
            progressed = True
            if len(picks) >= count:
                break
        if not progressed:
            break
        depth += 1

    result: list[tuple[TestCase, int, str]] = []
    seen_features: dict[str, int] = {}
    for case, sc in picks[:count]:
        seen = seen_features.get(case.feature, 0)
        seen_features[case.feature] = seen + 1
        position = "first pick" if seen == 0 else f"pick #{seen + 1}"
        result.append((case, sc, _rank_reason(case, position)))
    return result
