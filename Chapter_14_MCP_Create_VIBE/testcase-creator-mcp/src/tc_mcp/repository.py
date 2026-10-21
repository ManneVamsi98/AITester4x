"""Data layer: load, validate, normalize, index and merge the CSV source plus overlay."""

from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict
from typing import Optional

from tc_mcp.models import (
    BROWSERS,
    DEVICES,
    PRIORITIES,
    STATUSES,
    TEST_TYPES,
    Priority,
    Status,
    TestCase,
    TestCaseDraft,
    TestCaseChanges,
    TestFilter,
    TestType,
)
from tc_mcp.resolver import ModuleResolver

OVERLAY_FIELDS = [
    "Issue Type",
    "Issue Key",
    "Summary",
    "Description",
    "Priority",
    "Component",
    "Labels",
    "Test Type",
    "Preconditions",
    "Steps",
    "Expected Result",
    "Browser",
    "Device",
    "Status",
]


def _slug(text: str) -> str:
    text = text.lower().replace("/", " ").replace("&", " ")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def module_slug(module: str) -> str:
    if module == "A/B Testing":
        return "ab-testing"
    return _slug(module)


def normalize_labels(raw: str, module: str) -> list[str]:
    tokens = [t.strip() for t in raw.split() if t.strip()]
    if module == "A/B Testing" and tokens and tokens[0] == "a":
        tokens[0] = "ab-testing"
    deduped: list[str] = []
    for token in tokens:
        if not deduped or deduped[-1] != token:
            deduped.append(token)
    return deduped


def extract_feature(description: str, module: str, summary: Optional[str] = None) -> str:
    marker = f" in the {module} module"
    idx = description.lower().find(marker.lower())
    if idx != -1:
        before = description[:idx]
        parts = before.split(" the ")
        if parts:
            return parts[-1].strip()
    if summary:
        match = re.match(r"^\[.*?\]\s+[^:]+:\s*(.+)$", summary)
        if match:
            return match.group(1).strip()
    return ""


def split_steps(raw: str) -> list[str]:
    return [s.strip() for s in raw.split(" | ") if s.strip()]


def increment_key(issue_key: str) -> str:
    match = re.match(r"VWO-(\d+)$", issue_key)
    if not match:
        return issue_key
    return f"VWO-{int(match.group(1)) + 1}"


def _row_to_case(row: dict) -> TestCase:
    module = (row.get("Component") or "").strip()
    summary = (row.get("Summary") or "").strip()
    description = (row.get("Description") or "").strip()
    return TestCase(
        issue_key=(row.get("Issue Key") or "").strip(),
        summary=summary,
        description=description,
        priority=Priority((row.get("Priority") or "Low").strip()),
        module=module,
        feature=extract_feature(description, module, summary),
        labels=normalize_labels(row.get("Labels") or "", module),
        test_type=TestType((row.get("Test Type") or "Functional").strip()),
        preconditions=(row.get("Preconditions") or "").strip(),
        steps=split_steps(row.get("Steps") or ""),
        expected_result=(row.get("Expected Result") or "").strip(),
        browser=(row.get("Browser") or "").strip(),
        device=(row.get("Device") or "").strip(),
        status=Status((row.get("Status") or "Ready").strip()),
        scenario_id=summary,
    )


def _case_to_row(case: TestCase) -> dict:
    return {
        "Issue Type": "Test",
        "Issue Key": case.issue_key,
        "Summary": case.summary,
        "Description": case.description,
        "Priority": case.priority.value,
        "Component": case.module,
        "Labels": " ".join(case.labels),
        "Test Type": case.test_type.value,
        "Preconditions": case.preconditions,
        "Steps": " | ".join(case.steps),
        "Expected Result": case.expected_result,
        "Browser": case.browser,
        "Device": case.device,
        "Status": case.status.value,
    }


class Repository:
    def __init__(self, data_path: str, overlay_path: str):
        self.data_path = data_path
        self.overlay_path = overlay_path
        self.cases: list[TestCase] = []
        self.by_key: dict[str, TestCase] = {}
        self.modules: list[str] = []
        self.features_by_module: dict[str, list[str]] = {}
        self.resolver: ModuleResolver
        self._duplicate_keys: set[str] = set()
        self._duplicate_groups: list[list[TestCase]] = []
        self.reload()

    # -- loading ---------------------------------------------------------

    def _read_csv(self, path: str) -> list[dict]:
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def reload(self) -> None:
        base = [_row_to_case(r) for r in self._read_csv(self.data_path)]
        overlay = self._read_csv(self.overlay_path)

        merged: dict[str, TestCase] = {}
        for case in base:
            merged[case.issue_key] = case
        for row in overlay:
            key = (row.get("Issue Key") or "").strip()
            if key:
                merged[key] = _row_to_case(row)

        self.by_key = merged
        self.cases = sorted(merged.values(), key=lambda c: c.issue_key)
        self._mark_duplicates()
        self._build_indexes()

    def _mark_duplicates(self) -> None:
        groups: dict[tuple, list[TestCase]] = defaultdict(list)
        for case in self.cases:
            groups[(case.summary, case.browser, case.device)].append(case)
        self._duplicate_keys = set()
        self._duplicate_groups = []
        for members in groups.values():
            ordered = sorted(members, key=lambda c: c.issue_key)
            if len(ordered) > 1:
                self._duplicate_groups.append(ordered)
                for case in ordered[1:]:
                    self._duplicate_keys.add(case.issue_key)

    def _build_indexes(self) -> None:
        modules: dict[str, list[TestCase]] = defaultdict(list)
        for case in self.cases:
            modules[case.module].append(case)
        self.modules = sorted(modules.keys())
        self.resolver = ModuleResolver(self.modules)

        self.features_by_module = {}
        for module, cases in modules.items():
            features = sorted({c.feature for c in cases if c.feature})
            self.features_by_module[module] = features

    # -- queries ---------------------------------------------------------

    def is_duplicate(self, case: TestCase) -> bool:
        return case.issue_key in self._duplicate_keys

    def duplicate_groups(self, module: Optional[str] = None) -> list[list[TestCase]]:
        groups = self._duplicate_groups
        if module:
            canonical = self.resolver.resolve(module)
            groups = [g for g in groups if g[0].module == canonical]
        return groups

    def resolve_module(self, name: str) -> str:
        return self.resolver.resolve(name)

    def module_info(self, module: str) -> dict:
        cases = [c for c in self.cases if c.module == module]
        live = [c for c in cases if c.live]
        by_priority = Counter(c.priority.value for c in live)
        return {
            "module": module,
            "total": len(cases),
            "live": len(live),
            "by_priority": {p: by_priority.get(p, 0) for p in PRIORITIES},
            "features": self.features_by_module.get(module, []),
        }

    def live(self) -> list[TestCase]:
        return [c for c in self.cases if c.live]

    def filter(self, f: TestFilter) -> list[TestCase]:
        modules: Optional[set[str]] = None
        requested = []
        if f.module:
            requested.append(f.module)
        if f.modules:
            requested.extend(f.modules)
        if requested:
            modules = set(self.resolver.resolve_many(requested))

        result: list[TestCase] = []
        for case in self.cases:
            if not f.include_deprecated and not case.live:
                continue
            if not f.include_duplicates and self.is_duplicate(case):
                continue
            if modules is not None and case.module not in modules:
                continue
            if f.feature and f.feature.lower() not in case.feature.lower():
                continue
            if f.priority and case.priority not in f.priority:
                continue
            if f.min_priority or f.max_priority:
                idx = PRIORITIES.index(case.priority.value)
                if f.min_priority and idx < PRIORITIES.index(f.min_priority.value):
                    continue
                if f.max_priority and idx > PRIORITIES.index(f.max_priority.value):
                    continue
            if f.test_type and case.test_type not in f.test_type:
                continue
            if f.browser and case.browser != f.browser:
                continue
            if f.device and case.device != f.device:
                continue
            if f.status and case.status not in f.status:
                continue
            if f.label:
                joined = " ".join(case.labels).lower()
                if f.label.lower() not in joined:
                    continue
            result.append(case)
        return result

    def get(self, issue_key: str) -> Optional[TestCase]:
        return self.by_key.get(issue_key.strip().upper())

    def next_key(self) -> str:
        max_num = 6000
        for key in self.by_key:
            match = re.match(r"VWO-(\d+)$", key)
            if match:
                max_num = max(max_num, int(match.group(1)))
        return f"VWO-{max_num + 1}"

    def find_possible_duplicates(self, draft: TestCaseDraft) -> list[dict]:
        canonical = self.resolver.resolve(draft.module)
        feature = extract_feature(draft.description, canonical, draft.summary)
        matches = [
            c
            for c in self.cases
            if c.module == canonical
            and c.test_type == draft.test_type
            and (not feature or c.feature == feature)
        ][:5]
        return [
            {"key": c.issue_key, "summary": c.summary, "status": c.status.value}
            for c in matches
        ]

    def stats(self) -> dict:
        live = self.live()
        scenarios = {c.scenario_id for c in self.cases}
        return {
            "total_rows": len(self.cases),
            "live": len(live),
            "deprecated": sum(1 for c in self.cases if c.status == Status.Deprecated),
            "modules": len(self.modules),
            "features": sum(len(v) for v in self.features_by_module.values()),
            "scenarios": len(scenarios),
            "duplicate_rows": len(self._duplicate_keys),
            "priorities": dict(Counter(c.priority.value for c in self.cases)),
            "test_types": dict(Counter(c.test_type.value for c in self.cases)),
            "browsers": dict(Counter(c.browser for c in self.cases)),
            "devices": dict(Counter(c.device for c in self.cases)),
            "statuses": dict(Counter(c.status.value for c in self.cases)),
        }

    # -- writes (gated) --------------------------------------------------

    def _append_overlay(self, rows: list[dict]) -> None:
        write_header = not os.path.exists(self.overlay_path)
        parent = os.path.dirname(self.overlay_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.overlay_path, "a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OVERLAY_FIELDS)
            if write_header:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)
        self.reload()

    def add_cases(self, records: list[TestCase]) -> list[str]:
        rows = [_case_to_row(c) for c in records]
        self._append_overlay(rows)
        return [c.issue_key for c in records]

    def update_case(self, issue_key: str, changes: TestCaseChanges) -> tuple[TestCase, TestCase]:
        case = self.get(issue_key)
        if case is None:
            raise KeyError(issue_key)
        before = case.model_copy(deep=True)
        data = changes.model_dump(exclude_none=True)
        if "steps" in data and data["steps"] is not None:
            case.steps = data["steps"]
        for field in ("status", "priority", "expected_result", "summary", "description", "browser", "device"):
            if field in data and data[field] is not None:
                setattr(case, field, data[field])
        self._append_overlay([_case_to_row(case)])
        return before, case
