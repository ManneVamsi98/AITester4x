# QABuddy.ai — Phase 1 Hybrid RAG (Chapter 12)

## Goal

Build **QABuddy.ai** in `Chapter_12_RAG_QA_BuddyAI/`: a self-hosted, multi-source **Hybrid RAG** system so a QA engineer asks one question and gets **one cited answer** grounded in the Selenium framework, Playwright framework, ~5,000 test cases, JIRA history, PRDs/SRS/BRD, company docs, meeting notes, Lucid charts, and Jenkins logs.

Constraints (from the build prompt): embedding model + vector DB **open source**; **self-hosted** (DigitalOcean/VPS, internal); 24x7; token-efficient; every answer **cited**.

Confirmed choices: build the **full working Phase 1**; run Qdrant via **Docker Compose**; generate answers with **Groq**.

> Chapter 11's RAG used OpenAI embeddings + Pinecone — both disallowed by this prompt. QABuddy deliberately diverges and follows the Chapter 10 guide's "boring, works-in-production" recipe: **hybrid dense+sparse (RRF) + sentence-aware chunking + contextual retrieval + reranking**.

---

## Decisions (with justification)

### 1. Embedding model — `BAAI/bge-m3` (MIT, open source)
- **One model emits dense (1024-d) + sparse (lexical) vectors**, so dense + BM25-style sparse both come from the same model — exactly what hybrid search needs, no separate BM25 engine.
- Best all-round open model in our own Chapter 10 guide (`§16`); strong MTEB-retrieval; 8K context (fits larger code/PDF chunks); multilingual.
- Runs on CPU (acceptable for this corpus: ~5k test cases + docs + two repos). Served in-process via **FlagEmbedding** (`return_dense=True, return_sparse=True`).
- **Lighter fallback if the droplet is tiny:** `nomic-embed-text-v1.5` (768-d, ~550 MB) or `all-MiniLM-L6-v2` (384-d). Documented in README; default stays bge-m3.

### 2. Vector DB — `Qdrant` (Apache-2.0, self-host)
- Fully free to self-host (matches the free-only preference), Rust → fast and low-RAM for a small droplet.
- **Native hybrid search** (dense + sparse) with **RRF fusion** via `query_points(prefetch=[...], query=FusionQuery(Fusion.RRF))` — no Bolt-on BM25 service.
- Native **metadata filtering** (source type, repo, ticket key, date) and HNSW; official Docker image; named vectors `dense` + `sparse`.
- Rejected: Pinecone (proprietary), Chroma (no native sparse/hybrid), pgvector (manual BM25, no Postgres here yet).

### 3. Generation LLM — **Groq `openai/gpt-oss-120b`**
- Not part of the open-source constraint (only embedder + vector DB are). Free tier, fast, already the house default (Ch. 3/7/9). Needs `GROQ_KEY` in `.env`.
- Strict citation-forcing prompt: answer **only** from retrieved context; cite `[n] (file/ticket)`; otherwise say *"Insufficient evidence in the knowledge base."*

### 4. Reranker (bonus precision) — `BAAI/bge-reranker-v2-m3` (cross-encoder)
- Fetch top **20–30** candidates via hybrid, rerank to **5–8** for the LLM (Chapter 10 §9 recipe). Lighter `bge-reranker-base` documented as the low-RAM option.

### 5. Chunk size & overlap — **per source type**

| Source | Chunker | Chunk size | Overlap | Notes |
|---|---|---|---|---|
| Selenium/Playwright repos (code) | Declaration-aware (class/method/test blocks) | ~400–600 tokens | 10–15% | Keep file path, symbol, imports; metadata: repo, commit_sha, path |
| Test cases (CSV/XLSX) | **1 document per row** (Ch.11 `Key: value` assembly) | whole row | 0 | metadata: `tc_id`, category, priority, scenario_type... |
| PRD/SRS/BRD/FRD + company docs (PDF/MD) | Recursive character (markdown-header aware) | ~512 tokens | 15% | pdfplumber for tables; keep page + headings |
| Meeting notes/transcripts | Speaker-turn sliding window | ~300–500 tokens | 20% | Overlap preserves context |
| JIRA tickets | **1 document per ticket** (summary + ADF description + comments) | whole ticket | 0 | metadata: key, status, assignee, priority, labels, created |
| Lucid charts (text export) | Recursive by node/section | ~512 tokens | 15% | metadata: diagram name |
| Jenkins logs | Log-aware (build/test boundaries + header) | ~600–800 tokens | 10% | Strip ANSI, normalize timestamps |

**Advanced option (documented):** sentence-window / parent-child (index small, retrieve the larger parent).

### 6. Preprocessing / normalization
- **IDs are sacred:** never lowercase test-case IDs, JIRA keys, or error codes — sparse search must match `WING-LOGIN-TC-089` exactly.
- **Metadata on every point:** `source_type, source_file, path_or_url, page/section, repo, commit_sha, tc_id/jira_key, ingested_at, access_level`.
- **Per-format cleanup:** PDF → pdfplumber (tables, hyphenation, strip header/footer); logs → strip ANSI + normalize timestamps; CSV → strip embedded newlines; JIRA ADF → text; code → keep comments, normalize whitespace.
- **Contextual Retrieval (optional flag):** prefix each chunk with a 1-line Groq-generated context — Chapter 10: up to **67% fewer retrieval failures**.
- **Deterministic point IDs** (hash of source+path+index) so re-ingestion updates instead of duplicating.

---

## Architecture

```
                    ┌───────────────────────── Docker Compose ─────────────────────────┐
                    │                                                                  │
  data/ (10 sources)│   ┌───────────────┐        ┌──────────────────────────────────┐   │
  ────────────────► │   │  qdrant        │◄──────►│  app (Streamlit + qabuddy pkg)   │   │
                    │   │ (dense+sparse, │ upsert │  BGE-M3 embed (dense+sparse)     │   │
                    │   │  HNSW, filter) │ search │  bge-reranker-v2-m3              │   │
                    │   └───────────────┘        │  Groq generation (cited answer)  │   │
                    │        volume: qdrant_storage└──────────────────────────────────┘   │
                    └──────────────────────────────────────────────────────────────────┘

OFFLINE ingest:  load → clean → chunk (per source) → enrich metadata [+contextual] → embed → upsert
ONLINE query:    embed query → Qdrant hybrid (dense+sparse, RRF) top-25 → rerank → top-6 → Groq → cited answer
```

---

## Deliverables & folder structure

```
Chapter_12_RAG_QA_BuddyAI/
├─ plan.md                     # this approved plan
├─ prompt.md                   # the reusable build prompt
├─ README.md                   # overview, architecture, setup, run, deploy, verify
├─ docker-compose.yml          # qdrant + app services
├─ Dockerfile                  # app image (python:3.11-slim)
├─ .gitignore
├─ requirements.txt
├─ app.py                      # Streamlit chatbot (chat + citation cards + filters)
├─ qabuddy/
│  ├─ config.py                # env-driven settings
│  ├─ embeddings.py            # dense+sparse embedders (bge_m3 | ollama | hash)
│  ├─ sparse.py                # lexical sparse encoder
│  ├─ qdrant_store.py          # collection init, hybrid upsert/query (RRF), filters
│  ├─ chunking.py              # code / prose / logs / turns chunkers
│  ├─ cli.py                   # `python -m qabuddy.cli ingest --source all|<name>`
│  ├─ ingest/                  # base, testcases, repositories, documents,
│  │                           #   transcripts, diagrams, jenkins, jira
│  ├─ retrieval.py             # hybrid retrieve → rerank → citations
│  └─ rag.py                   # Groq cited-answer generation
├─ scripts/
│  ├─ ingest_all.py
│  └─ eval_retrieval.py        # recall@5/10 + MRR harness
├─ tests/test_pipeline.py      # dependency-free pipeline tests
├─ data/                       # the 10 source folders (contents gitignored)
│  ├─ 01_selenium_framework/ … 10_jenkins_logs/
└─ output/                     # eval reports + ingestion logs
```

---

## Implementation steps

1. Scaffold folders + config files.
2. Config + embeddings (+ sparse).
3. Qdrant store (named vectors, hybrid RRF, filters).
4. Chunkers.
5. Ingestion adapters (testcases first, then repositories, documents/transcripts/diagrams/jenkins, jira).
6. CLI + ingest_all.
7. Retrieval + RAG.
8. Streamlit app.
9. Dockerfile + docker-compose.
10. README + prompt.md.
11. Verify.
12. Commit.

---

## Data sources & adapters (10)

| # | Folder | Adapter | Now? |
|---|---|---|---|
| 1 | `01_selenium_framework` | `repositories.py` | Yes (public repo) |
| 2 | `02_playwright_framework` | `repositories.py` | Yes (public repo) |
| 3 | `03_test_cases` | `testcases.py` | Yes (Ch.11 CSV fixture) |
| 4 | `04_jira` | `jira.py` (MCP + JQL, REST fallback) | Adapter now; live when you share MCP config/JQL |
| 5 | `05_company_docs` | `documents.py` | Yes (pending files) |
| 6 | `06_figma_designs` | — | **Phase 2** |
| 7 | `07_meeting_notes` | `transcripts.py` | Yes (pending files) |
| 8 | `08_lucid_charts` | `diagrams.py` | Yes (pending files) |
| 9 | `09_prd_srs_brd` | `documents.py` | Yes (pending files) |
| 10 | `10_jenkins_logs` | `jenkins.py` | Yes (pending files) |

---

## Phase 2 — plan only

- **Hourly auto-ingestion:** scheduler diffs a manifest (file hashes / last commit SHA / JIRA `updated` JQL) and re-indexes only changed items (deterministic IDs make it idempotent).
- **Figma ingestion:** ER diagrams, user guides, wireframes → text (+ optional image captions).

---

## Deployment & sizing

- **Docker Compose** runs Qdrant + app (dev on Windows via Docker Desktop, prod on the droplet).
- **Sizing:** BGE-M3 (~2.3 GB) + reranker (~2.2 GB) resident → recommend **4 GB RAM / 2 vCPU** (~$24/mo DO). Cost-first: `nomic-embed-text-v1.5` + `bge-reranker-base` on **2 GB**. Free alternatives: Oracle Cloud Always Free, or local.
- Models cached in a Docker volume so restarts don't re-download.

---

## Verification

1. **Unit** — chunkers respect boundaries; `testcases.py` yields exactly **100** docs with unique `tc_id` from the Ch.11 CSV.
2. **Integration** — ingest the CSV; reuse Ch.11 checks: *"submit login with Enter"* → `WING-LOGIN-TC-002`; *"authentication-server-error"* → `WING-LOGIN-TC-089`.
3. **RAG behavior** — supported question → cited answer; unsupported → *"Insufficient evidence in the knowledge base."*
4. **Retrieval quality** — `scripts/eval_retrieval.py` prints recall@5 / recall@10 / MRR.
5. **App** — Streamlit bound to `127.0.0.1:8501`, `/_stcore/health` → 200, hand over `http://localhost:8501/`.
6. **Hygiene** — no `.env`, keys, or data blobs staged before commit.

---

## Assumptions & dependencies

- You place the Phase 1 data into `data/NN_*`; until then adapters run against the Ch.11 CSV and the two public repos.
- You share the **JIRA MCP connection + JQL**; `jira.py` is pluggable with a Jira REST fallback.
- **`GROQ_KEY`** supplied by you in `.env` (never committed).
- Docker available for the chosen Compose path.
- First run downloads bge-m3 + reranker (~4–5 GB) — one-time.

## Out of scope (Phase 1)

Hourly auto-ingestion and Figma ingestion (Phase 2); chatbot auth/SSO; the architecture diagram you mentioned (plan is self-contained; reconciled later if added).
