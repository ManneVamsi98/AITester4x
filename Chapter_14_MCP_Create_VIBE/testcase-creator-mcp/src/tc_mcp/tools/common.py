"""Shared helpers for tools: response envelope, pagination, sorting and detail."""

from __future__ import annotations

from typing import Any, Optional

from tc_mcp import config
from tc_mcp.models import PRIORITIES, TestCase


def envelope(
    total_matched: int,
    results: list[dict],
    offset: int,
    limit: int,
    filters_applied: Optional[dict] = None,
    note: Optional[str] = None,
) -> dict:
    payload: dict[str, Any] = {
        "total_matched": total_matched,
        "returned": len(results),
        "offset": offset,
        "next_offset": offset + len(results) if offset + len(results) < total_matched else None,
        "filters_applied": filters_applied or {},
        "results": results,
    }
    if note:
        payload["note"] = note
    return payload


def paginate(cases: list[TestCase], offset: int, limit: int) -> list[TestCase]:
    return cases[offset : offset + limit]


def sort_cases(cases: list[TestCase], sort_by: str) -> list[TestCase]:
    if sort_by == "key":
        return sorted(cases, key=lambda c: c.issue_key)
    priority_rank = {p: i for i, p in enumerate(PRIORITIES)}
    return sorted(cases, key=lambda c: (-priority_rank[c.priority.value], c.issue_key))


def compact_rows(cases: list[TestCase]) -> list[dict]:
    return [c.to_compact() for c in cases]


def full_rows(cases: list[TestCase]) -> list[dict]:
    return [c.to_full() for c in cases]


def detail_rows(cases: list[TestCase], detail: str) -> list[dict]:
    return full_rows(cases) if detail == "full" else compact_rows(cases)


def clamp_limit(limit: int, maximum: int) -> tuple[int, Optional[str]]:
    """Clamp a limit to its maximum and return (limit, note-if-clamped)."""
    if limit < 1:
        limit = 1
    if limit > maximum:
        return maximum, f"limit lowered to the maximum of {maximum}"
    return limit, None
