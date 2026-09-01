# SOP-02 — Normalize ticket (ADF → Markdown)

**Goal:** Convert the raw Jira payload into a normalized dict the LLM and tools consume.

**Inputs:** raw Jira issue JSON.

**Logic:**
1. Flatten `description` ADF → Markdown (`tools`/`jira_client.adf_to_md`): bullets, lists, headings, code blocks, tables.
2. Resolve `acceptance_criteria`:
   - explicit custom field (`acceptanceCriteria` / `Acceptance Criteria`), else
   - an "Acceptance Criteria" section parsed from the description Markdown.
3. Extract scalar fields: summary, status, issue_type, priority, labels, components, assignee, created, updated.

**Edge cases:**
- Plain-string description (Server/Data Center) → used as-is.
- Unknown ADF node types → unwrap to inner text (never crash).
- No acceptance criteria → empty string (readiness gate scores it low).

**Owner:** `jira_client.fetch_ticket`
