# SOP-03 — Readiness gate

**Goal:** Decide whether the ticket has enough substance to plan reliably.

**Inputs:** normalized ticket dict.

**Logic:** score 11 signals:
summary, description ≥ 40 chars, acceptance_criteria, status, issue_type,
priority, assignee, labels, components, created, description_rich
(has bullets or headings).

- `score < 5` → **refuse** with a gap report listing missing signals.
- `--force` (or the UI checkbox) overrides: gaps become assumptions.

**Edge cases:**
- Thin ticket + force → proceed, `collect_assumptions` notes every gap.
- Score is deterministic — same ticket always scores the same.

**Owner:** `tools.readiness_score`, `tools.readiness_gap_report`
