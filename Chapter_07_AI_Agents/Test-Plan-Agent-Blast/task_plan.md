# Task Plan — Test Plan Creator from a Jira ID

> B.L.A.S.T. Phase 1 (Blueprint) — Protocol 0 deliverable.
> **North Star:** From a single Jira ticket ID (e.g. `PROJ-123`), generate a structured, professional **Test Plan** document that mirrors the sections of the sample template (`Test Plan - Template.docx.pdf`): Objective, Scope, Inclusions, Test Environments, Defect Reporting, Test Strategy, Schedule, Deliverables, Entry/Exit Criteria, Test Execution, Closure, Tools, Risks & Mitigations, Approvals.

---

## 🎯 Goals (by B.L.A.S.T. Phase)

### Protocol 0 — Initialization (in progress)
- [x] Read `BLAST.md`, `Prompt_Used.md`, and the sample test plan PDF
- [x] Extract the sample PDF text to learn the exact test-plan section structure
- [ ] Answer the 5 Discovery questions (below) with the user
- [ ] Define the Input / Output JSON schema in `LLM.md` (Data-First Rule)
- [ ] Approve this Blueprint before any code is written

### Phase 2: L — Link (Connectivity)
- [ ] Confirm Jira instance type (Cloud vs Server/Data Center)
- [ ] Get Jira credentials (API token + email, or PAT) and store in `.env`
- [ ] Write `tools/jira_handshake.py` — a minimal GET to verify the connection
- [ ] Verify HTTP 200 + valid JSON for a real ticket ID

### Phase 3: A — Architect (3-Layer Build)
- [ ] Write `architecture/` SOP markdown (fetch-ticket SOP, map-to-plan SOP, render SOP)
- [ ] Write `tools/fetch_jira_ticket.py` — fetch issue JSON by ID
- [ ] Write `tools/build_test_plan.py` — map Jira fields → test plan sections (deterministic)
- [ ] Write `tools/render_test_plan.py` — output Markdown (and optionally DOCX/PDF)
- [ ] Use `.tmp/` for all intermediate files
- [ ] Unit-test each tool in isolation

### Phase 4: S — Stylize (Refinement & UI)
- [ ] Format the test plan for professional delivery (headings, tables, page breaks)
- [ ] Present the generated test plan to the user for feedback
- [ ] Iterate on style/sections per feedback

---

## 🔍 Discovery Questions (need answers before Phase 2)

1. **North Star:** Confirm the singular outcome — generate a test plan PDF/markdown from a Jira ID, correct?
2. **Integrations:** Which Jira instance? Is it Cloud (`*.atlassian.net`) or Server? Are credentials ready?
3. **Source of Truth:** The Jira ticket fields — which ones matter (summary, description, acceptance criteria, labels, components, issue type, status, attachments)?
4. **Delivery Payload:** Output format — Markdown, DOCX, or PDF? Where should it be delivered (local file, Notion, email)?
5. **Behavioral Rules:** Should the mapping from ticket → test plan be 100% deterministic (rules-based), or may an LLM draft prose sections? Any "Do Not" rules (e.g., never invent acceptance criteria)?

---

## 📋 Checklists

### Input validation
- [ ] Accept a Jira ID in the form `KEY-123`
- [ ] Reject empty / malformed IDs with a clear error

### Data mapping (ticket → plan)
- [ ] Summary → Test Plan title / Objective context
- [ ] Description → Scope + Inclusions
- [ ] Acceptance criteria → test cases outline
- [ ] Labels / components → risk areas + environments
- [ ] Issue type → test strategy hints (bug → regression; story → feature testing)
- [ ] Status / assignee → schedule + approvals

### Output
- [ ] Generate all template sections (even if some are "TBD")
- [ ] Consistent Markdown headings and tables
- [ ] (Optional) Convert to DOCX/PDF for delivery

---

## ⛔ Halt Condition (Protocol 0)

No scripts in `tools/` may be written until:
- Discovery questions are answered
- The JSON schema is defined in `LLM.md`
- This Blueprint is approved
