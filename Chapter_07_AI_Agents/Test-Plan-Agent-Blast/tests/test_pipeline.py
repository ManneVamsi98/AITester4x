#!/usr/bin/env python3
"""Offline pipeline tests for the Test Plan Agent.

No network, no model: fixtures + pure functions only.
Run:  python tests/test_pipeline.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
sys.path.insert(0, str(HERE))

import jira_client  # noqa: E402
import llm_client  # noqa: E402
import navigation  # noqa: E402
import render  # noqa: E402
from tools import (  # noqa: E402
    MIN_READINESS,
    collect_assumptions,
    default_scope_entries,
    readiness_gap_report,
    readiness_score,
    write_trace,
)

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"  FAIL: {name}")


def load(name):
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


rich = load("rich-ticket.json")
thin = load("thin-ticket.json")


def test_readiness():
    s, t, gaps = readiness_score(rich)
    check("rich score >= 5", s >= 5)
    check("rich total == 11", t == 11)
    check("rich has no gaps", gaps == [])

    s2, t2, g2 = readiness_score(thin)
    check("thin score < MIN_READINESS", s2 < MIN_READINESS)
    check("thin total == 11", t2 == 11)
    check("thin has gaps", len(g2) >= 5)

    report = readiness_gap_report(thin)
    check("gap report mentions readiness", "Readiness" in report)
    check("gap report lists missing signals", "description" in report)


def test_adf_conversion():
    # Bullet list + paragraph + hardBreak.
    adf = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]},
            {"type": "bulletList", "content": [{"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "one"}]}]}]},
        ],
    }
    md = jira_client.adf_to_md(adf)
    check("adf paragraph text", "Hello" in md)
    check("adf bullet", "- one" in md)

    # Marks: strong + code.
    adf2 = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
                {"type": "text", "text": "x", "marks": [{"type": "code"}]},
            ]},
        ],
    }
    md2 = jira_client.adf_to_md(adf2)
    check("adf strong mark", "**bold**" in md2)
    check("adf code mark", "`x`" in md2)

    # Unknown node type -> unwrap.
    adf3 = {"type": "doc", "content": [{"type": "mediaSingle", "content": [{"type": "text", "text": "img"}]}]}
    check("adf unknown node unwraps", "img" in jira_client.adf_to_md(adf3))

    # Heading levels.
    adf4 = {"type": "doc", "content": [{"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Title"}]}]}
    check("adf heading", "## Title" in jira_client.adf_to_md(adf4))

    # Plain string passthrough.
    check("plain string description", jira_client.plain_md("hello") == "hello")
    check("None description", jira_client.plain_md(None) == "")


def test_acceptance_extraction():
    desc = "## Acceptance criteria\n- AC1: do thing\n- AC2: do other\n## Other\nrest"
    ac = jira_client._extract_acceptance_criteria(desc)
    check("acceptance extracted", "AC1: do thing" in ac)
    check("acceptance excludes next section", "rest" not in ac)


def test_normalize_base_url():
    check("deep link trimmed", jira_client.normalize_base_url("https://x.atlassian.net/jira/software/projects/KAN/boards/1") == "https://x.atlassian.net")
    check("bare url ok", jira_client.normalize_base_url("https://x.atlassian.net") == "https://x.atlassian.net")
    check("missing scheme added", jira_client.normalize_base_url("x.atlassian.net") == "https://x.atlassian.net")
    check("empty url", jira_client.normalize_base_url("") == "")


def test_parse_key():
    check("bare key", navigation.parse_key("VWO-49") == "VWO-49")
    check("sentence key", navigation.parse_key("make a plan for VWO-49 please") == "VWO-49")
    try:
        navigation.parse_key("no key here")
        check("no key raises", False)
    except navigation.PipelineError as e:
        check("no key raises BAD_INPUT", e.code == navigation.BAD_INPUT)
    try:
        navigation.parse_key("")
        check("empty raises", False)
    except navigation.PipelineError:
        check("empty raises BAD_INPUT", True)


def test_scope_justified():
    entries = default_scope_entries(rich)
    check("scope has entries", len(entries) >= 5)
    check("every scope entry has justified_by", all(e.get("justified_by") for e in entries))
    check("AC justifies a scope entry", any("acceptance criteria" in e["justified_by"] for e in entries))


def test_assumptions():
    plan = {"scope": [{"entry": "Regression testing", "justified_by": "standard practice - no ticket fact contradicts it"}]}
    a = collect_assumptions(thin, plan)
    check("assumptions note standard practice", any("standard practice" in x for x in a))
    check("assumptions note missing AC", any("acceptance criteria" in x.lower() for x in a))

    a2 = collect_assumptions(rich, {"scope": default_scope_entries(rich)})
    check("rich ticket assumptions smaller", len(a2) < len(a))


def test_render():
    plan = {
        "objective": "Validate the flow.",
        "scope": [{"entry": "AC coverage", "justified_by": "acceptance criteria present"}],
        "environments": ["Staging"],
        "entry_criteria": ["Env ready"],
        "exit_criteria": ["All pass"],
        "test_cases": [{"id": "TC1", "title": "Cancel booking", "precondition": "Valid booking", "steps": ["Open widget", "Cancel"], "expected": "Status cancelled"}],
        "risks": [{"risk": "Payments", "mitigation": "Sandbox"}],
        "deliverables": ["Plan"],
        "assumptions": ["Payments assumed"],
    }
    md = render.render_plan_markdown(rich, plan)
    check("render has title", "Test Plan - Add cancellation flow" in md)
    check("render has objective", "Validate the flow." in md)
    check("render has justified scope", "justified by" in md)
    check("render has test case", "TC1 - Cancel booking" in md)
    check("render has steps", "1. Open widget" in md)
    check("render has assumptions", "## 9. Assumptions" in md)


def test_trace(tmp_path):
    meta = {"readiness": {"score": 9, "total": 11}, "model": "test", "duration_s": 0.1}
    p = write_trace(tmp_path, rich, {"objective": "x"}, meta)
    check("trace written", p.exists())
    data = json.loads(p.read_text(encoding="utf-8"))
    check("trace has ticket", data["ticket"]["key"] == "VWO-49")
    check("trace has readiness", data["readiness"]["score"] == 9)


def test_extract_json():
    check("plain json", llm_client._extract_json('{"a": 1}') == {"a": 1})
    check("fenced json", llm_client._extract_json('```json\n{"a": 1}\n```') == {"a": 1})
    check("prose + json", llm_client._extract_json('here: {"a": 1} done') == {"a": 1})
    try:
        llm_client._extract_json("no json")
        check("no json raises", False)
    except llm_client.LLMError:
        check("no json raises", True)


def main():
    test_readiness()
    test_adf_conversion()
    test_acceptance_extraction()
    test_normalize_base_url()
    test_parse_key()
    test_scope_justified()
    test_assumptions()
    test_render()
    test_trace(Path(HERE) / ".tmp" / "test-trace")
    test_extract_json()

    print(f"\n{len(FAILURES)} failures, {PASS} passed")
    if FAILURES:
        print("Failing:", *FAILURES, sep="\n  - ")
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
