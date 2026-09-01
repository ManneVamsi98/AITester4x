# SOP-05 — Render plan Markdown

**Goal:** Format the plan JSON into the final professional Markdown document.

**Inputs:** ticket dict + plan dict.

**Logic:** `render.render_plan_markdown` owns the template (the model never
sees it). Sections: Objective, Scope (with `justified_by`), Environments,
Entry/Exit Criteria, Test Cases, Risks & Mitigations, Deliverables,
Assumptions, source-ticket footer.

**Edge cases:**
- Empty arrays → "TBD" placeholders (never fabricated content).
- Long test-case step lists → numbered steps, preserved.

**Owner:** `render.py`
