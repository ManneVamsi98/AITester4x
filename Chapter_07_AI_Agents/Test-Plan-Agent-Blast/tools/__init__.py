"""Layer 3 tools - deterministic, atomic Python helpers for the Test Plan Agent.

Each function is a pure function (no I/O) unless noted. These are the
'deterministic six' of the seven-step pipeline; the only non-deterministic
step is the single Groq call in llm_client.
"""

import json
import os
import time
from pathlib import Path

# --- Readiness gate --------------------------------------------------------
# 11 signals we can check on a normalized ticket.
_READINESS_SIGNALS = (
    ("summary", lambda t: bool((t.get("summary") or "").strip())),
    ("description", lambda t: len((t.get("description") or "").strip()) >= 40),
    ("acceptance_criteria", lambda t: bool((t.get("acceptance_criteria") or "").strip())),
    ("status", lambda t: (t.get("status") or "") not in ("", "Not specified")),
    ("issue_type", lambda t: (t.get("issue_type") or "") not in ("", "Not specified")),
    ("priority", lambda t: (t.get("priority") or "") not in ("", "Not specified")),
    ("assignee", lambda t: (t.get("assignee") or "") not in ("", "Unassigned")),
    ("labels", lambda t: len(t.get("labels") or []) > 0),
    ("components", lambda t: len(t.get("components") or []) > 0),
    ("created", lambda t: bool(t.get("created"))),
    ("description_rich", lambda t: "\n- " in (t.get("description") or "") or "## " in (t.get("description") or "")),
)

MIN_READINESS = 5


def readiness_score(ticket: dict) -> tuple:
    """Return (score, total, gaps) for a normalized ticket.

    gaps is a list of signal names that failed, used to build the gap report.
    """
    score = 0
    gaps = []
    for name, fn in _READINESS_SIGNALS:
        if fn(ticket):
            score += 1
        else:
            gaps.append(name)
    return score, len(_READINESS_SIGNALS), gaps


def readiness_gap_report(ticket: dict) -> str:
    """Human-readable gap report for a thin ticket."""
    score, total, gaps = readiness_score(ticket)
    lines = [
        f"Readiness: {score}/{total} - below the {MIN_READINESS}/{total} threshold.",
        "",
        "This ticket is too thin to plan reliably. Add the missing details:",
    ]
    for g in gaps:
        lines.append(f"- {g}")
    lines.append("")
    lines.append("Re-run with --force to generate anyway (gaps become assumptions).")
    return "\n".join(lines)


# --- Scope justification ---------------------------------------------------
def default_scope_entries(ticket: dict) -> list:
    """Deterministic scope entries, each carrying justified_by (a ticket fact)."""
    entries = []
    facts = {
        "acceptance_criteria": "acceptance criteria present on the ticket",
        "description": "description present on the ticket",
        "issue_type": f"issue type is {ticket.get('issue_type')}",
        "components": "components listed on the ticket",
        "labels": "labels listed on the ticket",
    }

    if ticket.get("acceptance_criteria"):
        entries.append({"entry": "Acceptance-criteria coverage", "justified_by": facts["acceptance_criteria"]})
    if ticket.get("description"):
        entries.append({"entry": "Functional behaviour from description", "justified_by": facts["description"]})
    if ticket.get("issue_type"):
        entries.append({"entry": f"{ticket['issue_type']}-specific testing", "justified_by": facts["issue_type"]})
    if ticket.get("components"):
        entries.append({"entry": "Component integration checks", "justified_by": facts["components"]})
    if ticket.get("labels"):
        entries.append({"entry": "Label-flagged areas", "justified_by": facts["labels"]})

    # Always-present baseline entries with honest justification.
    entries.extend([
        {"entry": "Regression testing", "justified_by": "standard practice - no ticket fact contradicts it"},
        {"entry": "Error handling and boundary checks", "justified_by": "standard practice - no ticket fact contradicts it"},
    ])
    return entries


# --- Assumptions -----------------------------------------------------------
def collect_assumptions(ticket: dict, plan: dict) -> list:
    """Assumptions = plan claims not directly grounded in the ticket.

    Deterministic: for each scope entry, if its justified_by is the
    'standard practice' marker, we note it as an assumption.
    """
    assumptions = []
    for item in plan.get("scope", []):
        jb = item.get("justified_by", "")
        if "standard practice" in jb:
            assumptions.append(f"Scope item '{item.get('entry')}' is standard practice, not directly required by the ticket.")
    if not ticket.get("acceptance_criteria"):
        assumptions.append("Ticket has no explicit acceptance criteria; test cases derive from the description.")
    if not ticket.get("environments") and not ticket.get("components"):
        assumptions.append("No environments/components on the ticket; a default test environment matrix was assumed.")
    return assumptions


# --- Trace -----------------------------------------------------------------
def write_trace(out_dir: Path, ticket: dict, plan: dict, meta: dict) -> Path:
    """Write the -trace.json audit record next to the plan."""
    trace = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ticket": {k: ticket.get(k) for k in ("key", "url", "summary", "status", "issue_type", "priority", "labels", "components")},
        "readiness": meta.get("readiness"),
        "model": meta.get("model"),
        "duration_s": meta.get("duration_s"),
        "plan": plan,
    }
    path = out_dir / f"{ticket['key']}-trace.json"
    ensure_out_dir(out_dir)
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def ensure_out_dir(path: Path) -> None:
    os.makedirs(path, exist_ok=True)
