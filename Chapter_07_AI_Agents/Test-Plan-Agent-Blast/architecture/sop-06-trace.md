# SOP-06 — Trace & audit

**Goal:** Every generated plan ships with a `-trace.json` audit record so any
output can be traced back to its inputs.

**Inputs:** ticket dict, plan dict, meta (readiness, model, duration).

**Logic:**
1. Write `out/<key>.md` (the plan).
2. Write `out/<key>-trace.json`:
   - generated_at timestamp
   - ticket facts (key, url, summary, status, type, priority, labels, components)
   - readiness score/total
   - model name + duration
   - the full plan JSON.

**Edge cases:**
- `out/` is created on demand (gitignored).
- Trace is written even when the plan is mostly "TBD" — the audit stays honest.

**Owner:** `tools.write_trace`, `navigation.run_pipeline`
