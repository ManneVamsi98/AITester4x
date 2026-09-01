# LLM.md — Project Constitution (Schemas, Rules, Architecture)

> B.L.A.S.T. Protocol 0 — the **Project Constitution** for the Test Plan Agent.
> Data schemas, behavioral rules, and architectural invariants. If logic changes, update
> this file and the SOPs **before** changing code (Golden Rule).

---

## 1. Data Schemas

### 1.1 Input
```json
{
  "jira_id": "VWO-49"
}
```
Or a natural-language prompt containing the key.

### 1.2 Normalized ticket (after fetch + ADF→md)
```json
{
  "key": "VWO-49",
  "url": "https://vwo.atlassian.net/browse/VWO-49",
  "summary": "Add cancellation flow to booking widget",
  "description": "## Overview\nAs a user, I want to cancel a booking...",
  "acceptance_criteria": "AC1: ...",
  "status": "In Progress",
  "issue_type": "Story",
  "priority": "High",
  "labels": ["payments"],
  "components": ["Booking Service"],
  "assignee": "Vamsi",
  "created": "2026-08-01T10:00:00.000+0000",
  "updated": "2026-08-20T10:00:00.000+0000"
}
```

### 1.3 LLM output (STRICT JSON — the only non-deterministic step)
```json
{
  "objective": "string",
  "scope": [{"entry": "string", "justified_by": "string"}],
  "environments": ["string"],
  "test_cases": [{"id": "TC1", "title": "string", "precondition": "string", "steps": ["string"], "expected": "string"}],
  "entry_criteria": ["string"],
  "exit_criteria": ["string"],
  "risks": [{"risk": "string", "mitigation": "string"}],
  "deliverables": ["string"],
  "assumptions": ["string"]
}
```
`render.py` owns the final Markdown template; the model never sees it.

---

## 2. Behavioral Rules

1. **Six deterministic steps, one model call.** Parse → fetch → normalize → readiness → **Groq** → render. If the output is wrong, you can tell which step did it.
2. **Never invent anything.** No acceptance criterion, URL, date, or tool appears in the plan unless it is on the ticket. Everything else lands in `assumptions`.
3. **Scope is justified.** Every scope entry carries `justified_by` naming the ticket fact (or explicitly "standard practice"). Entries that cannot fill it are rejected.
4. **Readiness gate.** Below 5/11 the agent refuses with a gap report; `--force` overrides and gaps become assumptions.
5. **Model returns JSON, not Markdown.** `render.py` owns the format and cannot drift.
6. **Secrets in `.env`/config.json only.** Never hardcode, never commit.
7. **Golden Rule.** Update `LLM.md` + SOPs before changing code when logic changes.
8. **Fail loudly.** API errors map to exit codes 2–7; no silent empty plans.
9. **Every plan ships a trace.** `out/<key>-trace.json` records ticket facts, readiness, model, duration, and the plan JSON.

---

## 3. Architecture (B.L.A.S.T. / A.N.T. 3-Layer)

```
Test-Plan-Agent-Blast/
├── architecture/          # Layer 1: 6 SOPs (markdown)
│   ├── sop-01-fetch.md
│   ├── sop-02-normalize.md
│   ├── sop-03-readiness.md
│   ├── sop-04-generate.md
│   ├── sop-05-render.md
│   └── sop-06-trace.md
├── navigation.py          # Layer 2: routes data, exit codes, pipeline order
├── tools/                 # Layer 3: atomic Python (readiness, scope, assumptions, trace)
├── config_store.py        # config.json + .env seeding
├── jira_client.py         # REST v3 fetch + ADF→md
├── llm_client.py          # single Groq call (JSON)
├── render.py              # JSON plan → Markdown template
├── run.py                 # CLI (--health/--dry-run/--force)
├── app.py + pages/        # Streamlit UI
├── tests/ + fixtures/     # offline tests (45 checks)
├── out/                   # generated plans + traces (gitignored)
└── .env                   # secrets (gitignored)
```

- **Layer 1 — Architecture:** SOP markdown. If logic changes, the SOP changes first.
- **Layer 2 — Navigation:** the decision layer; calls tools in order, maps failures to exit codes.
- **Layer 3 — Tools:** atomic, deterministic Python; most are pure functions.

---

## 4. Edge cases (invariants)

- Empty description → readiness gap; `--force` → description-driven scope is skipped, assumption noted.
- No acceptance criteria → readiness gap; test cases derive from description only.
- 404 ticket → exit 4, readable error, no partial plan.
- Groq rate limit → exit 5; invalid JSON → exit 7.
- Model omits scope → deterministic justified scope replaces it.
