"""Layer 2 - navigation. Routes data between the deterministic tools and the
single LLM call. This module decides order, maps failures to exit codes, and
enforces the readiness gate.

Pipeline (7 steps, 6 deterministic + 1 model call):
    parse key -> fetch Jira -> normalize -> readiness -> Groq -> render -> write

Exit codes (documented in README):
    0 ok · 2 bad input · 3 auth · 4 not found · 5 rate limited ·
    6 schema violation · 7 LLM failure
"""

import re
import time
from pathlib import Path

import config_store
import jira_client
import llm_client
import render
from tools import (
    collect_assumptions,
    default_scope_entries,
    ensure_out_dir,
    readiness_gap_report,
    readiness_score,
    write_trace,
)
from tools import MIN_READINESS

JIRA_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")

# Exit codes
OK = 0
BAD_INPUT = 2
AUTH = 3
NOT_FOUND = 4
RATE_LIMITED = 5
SCHEMA_VIOLATION = 6
LLM_FAILURE = 7


class PipelineError(Exception):
    """Carries an exit code for the CLI."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def parse_key(prompt_or_key: str) -> str:
    """Extract a Jira key from a raw key or a natural-language prompt."""
    text = (prompt_or_key or "").strip()
    if not text:
        raise PipelineError(BAD_INPUT, "No input provided. Usage: run.py VWO-49")
    match = JIRA_KEY_RE.search(text)
    if not match:
        raise PipelineError(BAD_INPUT, f'Could not find a Jira ticket key in "{text}" (e.g. "make a plan for VWO-49").')
    return match.group(1)


def fetch_normalize(issue_key: str, cfg: dict) -> dict:
    """Steps 2-3: fetch + normalize. Maps Jira errors to exit codes."""
    try:
        return jira_client.fetch_ticket(issue_key, cfg)
    except jira_client.JiraError as exc:
        msg = str(exc)
        if "401" in msg or "credentials" in msg.lower():
            raise PipelineError(AUTH, msg) from exc
        if "404" in msg or "not found" in msg.lower():
            raise PipelineError(NOT_FOUND, msg) from exc
        raise PipelineError(BAD_INPUT, msg) from exc


def plan_from_ticket(ticket: dict, cfg: dict, force: bool = False) -> dict:
    """Steps 4-6: readiness gate, single Groq call, schema merge.

    Returns the final plan dict (merged with deterministic defaults so the
    document is complete even if the model returns a partial JSON).
    """
    score, total, gaps = readiness_score(ticket)
    if score < MIN_READINESS and not force:
        raise PipelineError(SCHEMA_VIOLATION, readiness_gap_report(ticket))

    started = time.time()
    raw = llm_client.generate_plan_json(ticket, cfg)
    duration = round(time.time() - started, 2)

    # Deterministic merge: ensure required keys + grounded scope.
    plan = {
        "objective": raw.get("objective") or f"Validate {ticket['key']} to ensure quality and reliability.",
        "scope": raw.get("scope") or default_scope_entries(ticket),
        "environments": raw.get("environments") or ["Development", "Staging", "Production"],
        "test_cases": raw.get("test_cases") or [],
        "entry_criteria": raw.get("entry_criteria") or ["Requirements stable", "Environment ready", "Test data available"],
        "exit_criteria": raw.get("exit_criteria") or ["All planned tests executed", "No open critical/high defects", "Metrics reviewed"],
        "risks": raw.get("risks") or [{"risk": "Missing ticket details", "mitigation": "Tracked in assumptions; clarify with product owner"}],
        "deliverables": raw.get("deliverables") or ["Test Plan (this document)", "Executed test cases", "Defect report"],
        "assumptions": raw.get("assumptions") or [],
    }

    # If the model returned no scope, use deterministic justified entries.
    if not raw.get("scope"):
        plan["scope"] = default_scope_entries(ticket)
    plan["assumptions"] = list(dict.fromkeys(plan["assumptions"] + collect_assumptions(ticket, plan)))
    return plan, {"readiness": {"score": score, "total": total}, "model": llm_client.GROQ_MODEL, "duration_s": duration}


def run_pipeline(prompt_or_key: str, cfg: dict, force: bool = False, dry_run: bool = False, out_dir: Path | None = None) -> dict:
    """Execute the full pipeline. Returns {ticket, plan, out_path, trace_path}.

    dry_run stops after fetch+normalize (no LLM call).
    """
    key = parse_key(prompt_or_key)
    ticket = fetch_normalize(key, cfg)

    if dry_run:
        return {"ticket": ticket, "plan": None, "out_path": None, "trace_path": None}

    plan, meta = plan_from_ticket(ticket, cfg, force=force)

    out_dir = out_dir or Path(__file__).parent / "out"
    ensure_out_dir(out_dir)
    out_path = out_dir / f"{key}.md"
    out_path.write_text(render.render_plan_markdown(ticket, plan), encoding="utf-8")
    trace_path = write_trace(out_dir, ticket, plan, meta)

    return {"ticket": ticket, "plan": plan, "out_path": out_path, "trace_path": trace_path}
