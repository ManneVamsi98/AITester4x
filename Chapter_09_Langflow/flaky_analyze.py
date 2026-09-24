"""Compare two Playwright JSON reports and count the flaky test cases.

A test is flaky when its pass/fail status differs between the two runs. A test that
fails in both runs is reported separately as consistently failing - that is a real
defect, not flakiness. Tests skipped in either run, tests present in only one run, and
tests that only passed because Playwright retried them within a run are also reported
separately and never add to the flaky total.

Usage:

    python Chapter_09_Langflow/flaky_analyze.py <folder> [--output-dir DIR]

`<folder>` must contain `result1.json` and `result2.json`. The two reports are written
into the folder as `flaky-report.md` and `flaky-report.json`.

Exit codes:

    0  analysed, no flaky tests
    1  analysed, flaky tests found
    2  bad input (folder or report file missing, unreadable, invalid, or not Playwright)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN1_NAME = "result1.json"
RUN2_NAME = "result2.json"
MD_NAME = "flaky-report.md"
JSON_NAME = "flaky-report.json"

TITLE_SEP = " › "
ASCII_SEP = " > "

PASSED = "passed"
FAILED = "failed"
SKIPPED = "skipped"

DECLARED_STATUS = {
    "expected": PASSED,
    "unexpected": FAILED,
    "flaky": PASSED,
    "skipped": SKIPPED,
}

EXIT_OK = 0
EXIT_FLAKY_FOUND = 1
EXIT_BAD_INPUT = 2


class InputError(Exception):
    """Raised when an input folder or report file cannot be used."""


def load_report(path: Path) -> dict:
    """Read and validate one Playwright JSON report."""
    if not path.is_file():
        raise InputError(f"missing required report file: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    if not text.strip():
        raise InputError(f"{path} is empty")
    try:
        report = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path} is not valid JSON: line {exc.lineno} column {exc.colno}: {exc.msg}") from exc
    if not isinstance(report, dict):
        raise InputError(f"{path} is not a Playwright JSON report (top level is not an object)")
    if "suites" not in report and "stats" not in report:
        raise InputError(f"{path} is not a Playwright JSON report (no 'suites' or 'stats' key)")
    if "suites" in report and not isinstance(report["suites"], list):
        raise InputError(f"{path} is not a Playwright JSON report ('suites' is not an array)")
    return report


def classify_test(test: dict, spec_ok: bool) -> tuple[str, bool]:
    """Return (status, retry_dependent) for one entry of a spec's `tests` array."""
    results = [r for r in (test.get("results") or []) if isinstance(r, dict)]
    declared = test.get("status")
    status = DECLARED_STATUS.get(declared) if isinstance(declared, str) else None
    if status is None:
        if results:
            last = results[-1].get("status")
            if last == "passed":
                status = PASSED
            elif last == "skipped":
                status = SKIPPED
            else:
                status = FAILED
        else:
            status = PASSED if spec_ok else FAILED
    retry_dependent = status == PASSED and (declared == "flaky" or len(results) > 1)
    return status, retry_dependent


def flatten_report(report: dict) -> list[dict]:
    """Walk the suite tree and return one record per test.

    Each record carries two candidate identities: `id_key` (Playwright's own id, empty
    when the export has none) and `path_key` (project + file + full title path).
    """
    records: list[dict] = []
    seen_paths: dict[str, int] = {}

    def walk(suite: dict, ancestors: list[str]) -> None:
        title = suite.get("title")
        path = ancestors + ([title] if isinstance(title, str) and title else [])
        file = suite.get("file") or (path[0] if path else "")

        for spec in suite.get("specs") or []:
            if not isinstance(spec, dict):
                continue
            spec_title = spec.get("title") or ""
            title_path = TITLE_SEP.join([*path, spec_title]) if spec_title else TITLE_SEP.join(path)
            spec_id = spec.get("id")
            spec_ok = bool(spec.get("ok", True))

            for test in spec.get("tests") or []:
                if not isinstance(test, dict):
                    continue
                status, retry_dependent = classify_test(test, spec_ok)
                project = test.get("projectName") or ""

                path_key = f"{project} :: {file} :: {title_path}"
                seen_paths[path_key] = seen_paths.get(path_key, 0) + 1
                if seen_paths[path_key] > 1:
                    path_key = f"{path_key}#{seen_paths[path_key]}"

                test_id = test.get("id")
                if isinstance(test_id, str) and test_id.strip():
                    id_key = test_id
                elif isinstance(spec_id, str) and spec_id.strip():
                    id_key = f"{spec_id} :: {project}" if project else spec_id
                else:
                    id_key = ""

                records.append(
                    {
                        "id_key": id_key,
                        "path_key": path_key,
                        "title": spec_title,
                        "title_path": title_path,
                        "file": str(file),
                        "project": str(project),
                        "status": status,
                        "retry_dependent": retry_dependent,
                    }
                )

        for child in suite.get("suites") or []:
            if isinstance(child, dict):
                walk(child, path)

    for suite in report.get("suites") or []:
        if isinstance(suite, dict):
            walk(suite, [])

    return records


def choose_join(records1: list[dict], records2: list[dict]) -> str:
    """Decide whether the two runs are matched by id or by file + title path.

    Playwright ids are stable across runs, so they are preferred on a tie. When the ids
    line up worse than the title paths do, the ids are not comparable (for example the
    reports came from different test id schemes) and the path key is the honest join.
    """
    ids1 = {r["id_key"] for r in records1 if r["id_key"]}
    ids2 = {r["id_key"] for r in records2 if r["id_key"]}
    paths1 = {r["path_key"] for r in records1}
    paths2 = {r["path_key"] for r in records2}
    return "path" if len(paths1 & paths2) > len(ids1 & ids2) else "id"


def index_records(records: list[dict], join: str) -> dict[str, dict]:
    """Key records for comparison, falling back to the path key when an id is missing."""
    indexed: dict[str, dict] = {}
    for record in records:
        key = (record["id_key"] if join == "id" else "") or record["path_key"]
        unique = key
        suffix = 1
        while unique in indexed:
            suffix += 1
            unique = f"{key}#{suffix}"
        indexed[unique] = record
    return indexed


def join_warnings(join: str, records1: list[dict], records2: list[dict]) -> list[str]:
    """Warn when ids were available but could not be used to match the two runs."""
    if join != "path":
        return []
    if any(r["id_key"] for r in records1) and any(r["id_key"] for r in records2):
        return [
            "the two runs share no test ids; tests were matched by project + file + title path instead"
        ]
    return []


def summarise(records: dict[str, dict]) -> dict:
    """Count each status across one run."""
    counts = {PASSED: 0, FAILED: 0, SKIPPED: 0}
    retry_dependent = 0
    for record in records.values():
        counts[record["status"]] += 1
        if record["retry_dependent"]:
            retry_dependent += 1
    return {
        "total": len(records),
        "passed": counts[PASSED],
        "failed": counts[FAILED],
        "skipped": counts[SKIPPED],
        "retry_dependent": retry_dependent,
    }


def stats_warnings(label: str, report: dict, summary: dict) -> list[str]:
    """Compare our parsed counts against the report's own `stats` block."""
    stats = report.get("stats")
    if not isinstance(stats, dict):
        return []

    warnings: list[str] = []
    expected = stats.get("expected")
    flaky = stats.get("flaky")
    unexpected = stats.get("unexpected")
    skipped = stats.get("skipped")

    if isinstance(expected, int) and isinstance(flaky, int):
        if summary["passed"] != expected + flaky:
            warnings.append(
                f"{label}: parsed {summary['passed']} passed but its stats block reports "
                f"{expected} expected + {flaky} flaky"
            )
    if isinstance(unexpected, int) and summary["failed"] != unexpected:
        warnings.append(f"{label}: parsed {summary['failed']} failed but its stats block reports {unexpected} unexpected")
    if isinstance(skipped, int) and summary["skipped"] != skipped:
        warnings.append(f"{label}: parsed {summary['skipped']} skipped but its stats block reports {skipped}")

    return warnings


def _entry(key: str, record: dict, run1_status: str | None, run2_status: str | None) -> dict:
    return {
        "key": key,
        "path_key": record["path_key"],
        "title": record["title"],
        "title_path": record["title_path"],
        "file": record["file"],
        "project": record["project"],
        "run1": run1_status,
        "run2": run2_status,
    }


def _sort(entries: list[dict]) -> list[dict]:
    return sorted(entries, key=lambda e: (e["file"], e["title_path"], e["project"]))


def compare(records1: dict[str, dict], records2: dict[str, dict]) -> dict:
    """Partition tests shared by both runs into flaky / consistent / skipped buckets."""
    flaky: list[dict] = []
    consistently_failing: list[dict] = []
    consistently_passing: list[dict] = []
    skipped: list[dict] = []
    retry_dependent: list[dict] = []

    for key in sorted(set(records1) & set(records2)):
        first, second = records1[key], records2[key]
        entry = _entry(key, first, first["status"], second["status"])

        if first["status"] == SKIPPED or second["status"] == SKIPPED:
            skipped.append(entry)
        elif first["status"] == PASSED and second["status"] == PASSED:
            consistently_passing.append(entry)
        elif first["status"] == FAILED and second["status"] == FAILED:
            consistently_failing.append(entry)
        else:
            entry["direction"] = "regressed" if second["status"] == FAILED else "recovered"
            flaky.append(entry)

        if first["retry_dependent"] or second["retry_dependent"]:
            retry_dependent.append(entry)

    only_in_run1 = _sort([_entry(k, records1[k], records1[k]["status"], None) for k in sorted(set(records1) - set(records2))])
    only_in_run2 = _sort([_entry(k, records2[k], None, records2[k]["status"]) for k in sorted(set(records2) - set(records1))])

    flaky = _sort(flaky)
    return {
        "flaky": flaky,
        "flaky_count": len(flaky),
        "regressed_count": sum(1 for e in flaky if e["direction"] == "regressed"),
        "recovered_count": sum(1 for e in flaky if e["direction"] == "recovered"),
        "consistently_failing": _sort(consistently_failing),
        "consistently_passing": _sort(consistently_passing),
        "skipped": _sort(skipped),
        "retry_dependent": _sort(retry_dependent),
        "only_in_run1": only_in_run1,
        "only_in_run2": only_in_run2,
    }


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _describe(entry: dict) -> str:
    location = f"[{entry['file']}] {entry['title_path']}" if entry["file"] else entry["title_path"]
    return f"{location} ({entry['project']})" if entry["project"] else location


def render_markdown(comparison: dict, meta1: dict, meta2: dict) -> str:
    """Own the Markdown report template."""
    summary1, summary2 = meta1["summary"], meta2["summary"]
    lines = [
        f"# Flaky Test Report — {comparison['folder_name']}",
        "",
        f"**Run 1:** `{meta1['file']}` · {summary1['total']} tests · {summary1['passed']} passed / "
        f"{summary1['failed']} failed / {summary1['skipped']} skipped",
        "",
        f"**Run 2:** `{meta2['file']}` · {summary2['total']} tests · {summary2['passed']} passed / "
        f"{summary2['failed']} failed / {summary2['skipped']} skipped",
        "",
        f"**Flaky test cases found: {comparison['flaky_count']}**",
        "",
        "## 1. Summary",
        "",
    ]

    lines.extend(
        _table(
            ["Metric", "Count"],
            [
                ["**Flaky (status flipped between the two runs)**", f"**{comparison['flaky_count']}**"],
                ["↳ regressed (passed then failed)", str(comparison["regressed_count"])],
                ["↳ recovered (failed then passed)", str(comparison["recovered_count"])],
                ["Consistently failing (failed in both runs)", str(len(comparison["consistently_failing"]))],
                ["Consistently passing", str(len(comparison["consistently_passing"]))],
                ["Skipped in at least one run", str(len(comparison["skipped"]))],
                ["Present in only one run (not comparable)", str(len(comparison["only_in_run1"]) + len(comparison["only_in_run2"]))],
                ["Retry-dependent within a run (not counted as flaky)", str(len(comparison["retry_dependent"]))],
            ],
        )
    )

    lines.extend(["", "## 2. Flaky tests", ""])
    if comparison["flaky"]:
        lines.extend(
            _table(
                ["#", "Test", "File", "Project", "Run 1", "Run 2", "Direction"],
                [
                    [
                        str(index),
                        _cell(entry["title_path"]),
                        _cell(entry["file"]),
                        _cell(entry["project"]),
                        entry["run1"],
                        entry["run2"],
                        entry["direction"],
                    ]
                    for index, entry in enumerate(comparison["flaky"], start=1)
                ],
            )
        )
    else:
        lines.append("None. No test changed status between the two runs.")

    lines.extend(["", "## 3. Consistently failing (not flaky — deterministic defects)", ""])
    if comparison["consistently_failing"]:
        lines.extend(
            _table(
                ["#", "Test", "File", "Project", "Run 1", "Run 2"],
                [
                    [str(index), _cell(e["title_path"]), _cell(e["file"]), _cell(e["project"]), e["run1"], e["run2"]]
                    for index, e in enumerate(comparison["consistently_failing"], start=1)
                ],
            )
        )
    else:
        lines.append("None.")

    lines.extend(["", "## 4. Skipped, single-run, and retry-dependent tests", ""])

    def subsection(heading: str, entries: list[dict], note: str) -> None:
        lines.extend([f"### {heading}", ""])
        if entries:
            lines.extend(
                _table(
                    ["#", "Test", "File", "Project", "Run 1", "Run 2"],
                    [
                        [str(i), _cell(e["title_path"]), _cell(e["file"]), _cell(e["project"]), e["run1"] or "—", e["run2"] or "—"]
                        for i, e in enumerate(entries, start=1)
                    ],
                )
            )
        else:
            lines.append(note)

    subsection("Skipped in either run", comparison["skipped"], "None.")
    lines.append("")
    subsection("Present in run 1 only", comparison["only_in_run1"], "None.")
    lines.append("")
    subsection("Present in run 2 only", comparison["only_in_run2"], "None.")
    lines.append("")
    subsection(
        "Retry-dependent within a run",
        comparison["retry_dependent"],
        "None. No test needed an in-run retry to pass.",
    )

    lines.extend(
        [
            "",
            "## 5. Method",
            "",
            "- **Flaky** means the test's status differed between the two runs: it passed in one and "
            "failed in the other. Both directions count (regressed and recovered).",
            "- **Consistently failing** tests failed in both runs. They are deterministic defects, not "
            "flakiness, so they are reported separately and excluded from the flaky count.",
            "- Tests skipped in either run, and tests present in only one run, are excluded from the "
            "flaky count.",
            "- **Retry-dependent** marks tests that only passed because Playwright retried them inside a "
            "single run. They are listed for visibility but do not add to the flaky count.",
            "- A failure status covers `failed`, `timedOut`, and `interrupted`.",
            f"- Tests were matched by **{comparison['matched_by']}**. Playwright's test id is used "
            "when the two runs share ids; otherwise tests are matched by project + file + full title path.",
            "- The parsed pass/fail/skip counts are cross-checked against each report's own `stats` "
            "block, and any mismatch is reported as a warning.",
            "",
            "---",
            f"*Generated {comparison['generated_at']} by Chapter_09_Langflow/flaky_analyze.py.*",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(comparison: dict, meta1: dict, meta2: dict) -> dict:
    """Build the machine-readable result."""
    return {
        "generated_at": comparison["generated_at"],
        "folder": comparison["folder"],
        "matched_by": comparison["matched_by"],
        "run1": meta1,
        "run2": meta2,
        "flaky_count": comparison["flaky_count"],
        "regressed_count": comparison["regressed_count"],
        "recovered_count": comparison["recovered_count"],
        "flaky": comparison["flaky"],
        "consistently_failing": comparison["consistently_failing"],
        "consistently_passing_count": len(comparison["consistently_passing"]),
        "skipped": comparison["skipped"],
        "only_in_run1": comparison["only_in_run1"],
        "only_in_run2": comparison["only_in_run2"],
        "retry_dependent": comparison["retry_dependent"],
    }


def analyze_paths(path1: Path, path2: Path) -> dict:
    """Load two Playwright reports and produce the comparison plus per-run metadata.

    Pure: no printing, no file writes. Shared by the command line tool and the Langflow
    component so both report identical numbers.
    """
    report1 = load_report(path1)
    report2 = load_report(path2)

    flat1 = flatten_report(report1)
    flat2 = flatten_report(report2)
    join = choose_join(flat1, flat2)
    records1 = index_records(flat1, join)
    records2 = index_records(flat2, join)
    summary1 = summarise(records1)
    summary2 = summarise(records2)

    comparison = compare(records1, records2)
    comparison["matched_by"] = "test id" if join == "id" else "project + file + title path"
    comparison["folder"] = str(path1.parent)
    comparison["folder_name"] = path1.parent.name or str(path1.parent)
    comparison["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    warnings = (
        join_warnings(join, flat1, flat2)
        + stats_warnings(path1.name, report1, summary1)
        + stats_warnings(path2.name, report2, summary2)
    )

    return {
        "comparison": comparison,
        "meta1": {"file": path1.name, "path": str(path1), "summary": summary1, "stats": report1.get("stats")},
        "meta2": {"file": path2.name, "path": str(path2), "summary": summary2, "stats": report2.get("stats")},
        "warnings": warnings,
    }


def summary_lines(analysis: dict) -> list[str]:
    """Render the human-readable summary shared by the CLI and the Langflow component."""
    comparison = analysis["comparison"]
    meta1, meta2 = analysis["meta1"], analysis["meta2"]
    summary1, summary2 = meta1["summary"], meta2["summary"]

    lines = [
        f"Folder: {comparison['folder']}",
        f"  {meta1['file']}: {summary1['total']} tests — {summary1['passed']} passed, "
        f"{summary1['failed']} failed, {summary1['skipped']} skipped",
        f"  {meta2['file']}: {summary2['total']} tests — {summary2['passed']} passed, "
        f"{summary2['failed']} failed, {summary2['skipped']} skipped",
        f"  matched by: {comparison['matched_by']}",
    ]
    lines.extend(f"  [warning] {warning}" for warning in analysis["warnings"])

    lines.extend(["", f"Flaky: {comparison['flaky_count']}"])
    lines.extend(
        f"  - {_describe(entry).replace(TITLE_SEP, ASCII_SEP)}  "
        f"run1: {entry['run1']} -> run2: {entry['run2']}  ({entry['direction']})"
        for entry in comparison["flaky"]
    )

    lines.extend(["", f"Consistently failing (not flaky): {len(comparison['consistently_failing'])}"])
    lines.extend(
        f"  - {_describe(entry).replace(TITLE_SEP, ASCII_SEP)}" for entry in comparison["consistently_failing"]
    )

    if comparison["only_in_run1"] or comparison["only_in_run2"]:
        lines.extend(
            [
                "",
                f"Not comparable (present in one run only): "
                f"{len(comparison['only_in_run1'])} in {meta1['file']}, "
                f"{len(comparison['only_in_run2'])} in {meta2['file']}",
            ]
        )

    return lines


def run(folder: Path, output_dir: Path) -> int:
    """Analyse one folder and write the reports."""
    if not folder.is_dir():
        raise InputError(f"not a folder: {folder}")

    path1 = folder / RUN1_NAME
    path2 = folder / RUN2_NAME
    analysis = analyze_paths(path1, path2)
    comparison = analysis["comparison"]
    meta1, meta2 = analysis["meta1"], analysis["meta2"]

    comparison["folder"] = str(folder)
    comparison["folder_name"] = folder.name or str(folder)

    markdown = render_markdown(comparison, meta1, meta2)
    payload = build_payload(comparison, meta1, meta2)
    payload["warnings"] = analysis["warnings"]

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / MD_NAME).write_text(markdown, encoding="utf-8")
    (output_dir / JSON_NAME).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for line in summary_lines(analysis):
        print(line)

    print()
    print(f"Wrote {output_dir / MD_NAME}")
    print(f"Wrote {output_dir / JSON_NAME}")

    return EXIT_FLAKY_FOUND if comparison["flaky_count"] else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, analyse the folder, and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="flaky_analyze.py",
        description="Compare two Playwright JSON reports and count the flaky test cases.",
    )
    parser.add_argument("folder", type=Path, help=f"folder containing {RUN1_NAME} and {RUN2_NAME}")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="where to write the reports (default: the same folder)",
    )
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    output_dir = args.output_dir or args.folder
    try:
        return run(args.folder, output_dir)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except OSError as exc:
        print(f"error: cannot write reports to {output_dir}: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT


if __name__ == "__main__":
    raise SystemExit(main())
