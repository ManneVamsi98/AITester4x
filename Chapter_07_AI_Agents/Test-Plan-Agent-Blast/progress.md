# Progress — Test Plan Creator from a Jira ID

> B.L.A.S.T. protocol log: what was done, what failed, what resulted. Appended as work proceeds.

---

## Session 1 — Protocol 0 (Blueprint docs)

### 10:00 — Read the chapter inputs
- **Done:** Read `BLAST.md`, `Prompt_Used.md`, and the sample `Test Plan - Template.docx.pdf`.
- **Finding:** The objective is to build a **test plan creator from a Jira ID**; Protocol 0 requires planning docs before any code.
- **Result:** Created `task_plan.md`, `findings.md`, `progress.md`, `LLM.md` blueprint.

### 10:15 — Extract sample test plan structure
- **Done:** Attempted PDF text extraction.
- **Error:** `pdftotext` not installed; `pypdf` not present. Installed `pypdf` (6.16.2).
- **Error (2):** First extraction crashed on console encoding (`UnicodeEncodeError` — `\u25cf` bullet). 
- **Fix:** Wrote extracted text to a UTF-8 file instead of printing.
- **Result:** Got the full 14-section template structure (Objective → Approvals) — the exact layout the generator must produce. Captured in `findings.md`.

### 10:30 — Document the Jira API approach
- **Done:** Researched Jira Cloud REST API (`/rest/api/3/issue/{key}`), auth (Basic email+token, Bearer PAT), and JQL search.
- **Result:** Recorded working curl examples and field→section mapping in `findings.md`.

### 10:45 — Define schema + rules
- **Done:** Wrote `LLM.md` with Input/Output JSON schemas, behavioral rules, and the 3-layer architecture (per BLAST).
- **Result:** Data-First Rule satisfied — schema approved before code.

### Next steps (Phase 2 — Link, pending answers)
- [ ] Get Jira instance URL + credentials from user, store in `.env`
- [ ] `tools/jira_handshake.py` — verify connection returns 200
- [ ] Then Phase 3 (Architect) and Phase 4 (Stylize)

---

## Known open items / risks
- **Acceptance-criteria custom field id** varies per Jira instance — resolve dynamically, don't hardcode.
- **Secrets** must live in `.env` (gitignored), never in code or docs.
- **Deterministic mapping** — no LLM guessing on business logic (BLAST Golden Rule).
