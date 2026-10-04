# QABuddy.ai — Build Prompt (reusable)

The prompt that generated this chapter's deliverable. Reuse it to reproduce or extend the build.
The original source is [`QABUDDY_Improved_.prompt.md`](./QABUDDY_Improved_.prompt.md).

## Role

Act as a senior AI engineer. Design and build **QABuddy.ai** — a self-hosted, multi-source
**Hybrid RAG** (Retrieval-Augmented Generation) system for QA engineers.

## Objective

A QA engineer asks one question and gets a single **cited answer** grounded in the Selenium
framework, Playwright framework, VWO test-case repository, PRDs, and JIRA bug history.

The end-to-end system must:

1. Ingest code and documents from a defined folder structure (Phase 1).
2. Chunk, embed, and index them in an **open-source vector database** with hybrid
   (keyword + semantic) retrieval.
3. Serve grounded answers **with citations** through a chatbot.
4. Run 24x7 on a DigitalOcean droplet (or similar VPS / self-hosted server).
5. Keep token usage low by retrieving only relevant context.

## Data sources (10)

One folder per source:

1. Selenium framework repo — `https://github.com/PramodDutta/ATB13xSeleniumAdvanceFramework`
2. Playwright framework repo — `https://github.com/PramodDutta/Advance-Playwright-Framework`
3. Test cases (~5,000) — CSV / XLSX
4. JIRA tickets — live via **JIRA MCP connection + JQL**
5. Company docs — PDF, MD
6. Figma designs — exports **(Phase 2)**
7. Meeting notes & recordings — text transcripts
8. Lucid charts — exported to text
9. PRD / SRS / BRD / FRD — PDF
10. Jenkins logs & results — log / text files

## Phase 1 — build now

1. Folder structure for all 10 sources.
2. Ingestion pipeline: parse → clean → chunk → embed → index, with source-appropriate handling.
3. Connect to JIRA (MCP + JQL) and ingest all matching tickets.
4. Hybrid retrieval with citations — every answer references its source file / ticket.
5. Chatbot layer deployable to the VPS.

## Phase 2 — plan only

- Hourly auto-ingestion: detect new test cases, commits, or documents and re-index hourly.
- Figma design ingestion.

## Decisions to make (with justification)

1. Which open-source embedding model?
2. Which open-source vector database?
3. Accurate chunk size and overlap per source type (code, test-case rows, PDFs, transcripts, logs)?
4. Preprocessing / normalization (terminology, metadata, cleanup)?
5. Overall architecture, structure, and plan?

## Constraints

- Embedding model and vector DB must be **open source**.
- **Self-hosted** on a droplet / VPS, internal use.
- Available 24x7 and token-efficient.

## How to respond

Before writing any code: present the full plan and architecture with reasoning, justify the
embedding model, vector DB, chunk size and overlap choices, and show the proposed folder structure.
Wait for approval, then implement Phase 1 end-to-end.

---

### Chosen in this build (see `plan.md` for the reasoning)

- Embeddings: `BAAI/bge-m3` (open source, dense + native sparse).
- Vector DB: **Qdrant** (Apache-2.0, native hybrid + RRF).
- Rerank: `BAAI/bge-reranker-v2-m3` cross-encoder.
- Generation: **Groq** `openai/gpt-oss-120b`.
- Runtime: **Docker Compose** (Qdrant + Streamlit app), droplet-ready.
