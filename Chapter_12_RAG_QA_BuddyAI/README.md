# QABuddy.ai — Phase 1

A self-hosted, multi-source **Hybrid RAG** system for QA engineers. Ask one question, get
**one cited answer** grounded in framework code, test cases, JIRA, PRDs, company docs, meeting
notes, Lucid charts, and Jenkins logs.

- **Open-source stack:** `BAAI/bge-m3` embeddings + **Qdrant** vector DB (Apache-2.0).
- **Hybrid retrieval:** dense + lexical sparse, fused with Reciprocal Rank Fusion, then a
  cross-encoder rerank.
- **Grounded answers:** Groq generation that must cite `[n]` sources or reply
  *"Insufficient evidence in the knowledge base."*
- **Runs anywhere Docker runs** — local Docker Desktop for dev, a DigitalOcean/VPS droplet for 24x7.

The design rationale lives in [`plan.md`](./plan.md); the reusable build prompt is in
[`prompt.md`](./prompt.md).

---

## Architecture

```
data/ (10 sources)
   │  ingest: load → clean → chunk (per source) → enrich metadata → embed → upsert
   ▼
┌─────────────┐   dense + sparse    ┌──────────────────────────────────────┐
│   Qdrant     │◄───────────────────►│  Streamlit app + qabuddy package     │
│  HNSW+filter │   hybrid (RRF)      │  bge-m3 · bge-reranker · Groq        │
└─────────────┘                     └──────────────────────────────────────┘
   query: embed → hybrid top-K → rerank → top-N → Groq → cited answer
```

---

## Quickstart (Docker)

```bash
# 1. Configure — create .env (gitignored) and set GROQ_KEY (+ optional JIRA_*)

# 2. Start Qdrant + the app  (first run downloads ~4-5 GB of models)
docker compose up -d --build

# 3. Index the sources (put your data in data/** first — see data/*/README.md)
docker compose run --rm app python -m qabuddy.cli ingest --source all

# 4. Open the chatbot
#    http://localhost:8501/
```

`docker compose` maps the UI to `127.0.0.1:8501` (loopback only) and Qdrant to
`127.0.0.1:6333`.

---

## Run locally without Docker (Ollama embeddings)

For a machine without Docker/torch (e.g. Python 3.14, where `bge-m3` can't install), run
Qdrant from its standalone binary and embed via a local **Ollama** server:

```bash
# 1. Qdrant binary (~40 MB) — extract so you have .tools/qdrant/qdrant.exe
#    https://github.com/qdrant/qdrant/releases  (qdrant-x86_64-pc-windows-msvc.zip)

# 2. Embedding model (768-d)
ollama pull nomic-embed-text

# 3. Light deps (no torch)
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-local.txt

# 4. Configure: .env with EMBED_PROVIDER=ollama, RERANK_ENABLED=false, GROQ_KEY=...

# 5. Ingest, then launch everything
.venv\Scripts\python.exe -m qabuddy.cli ingest --source all
scripts\run_local.cmd            # starts Qdrant + Streamlit
```

`run_local.cmd` starts Qdrant on `127.0.0.1:6333` then the app at **http://localhost:8501/**.
Reranking is off in this profile (it needs torch); retrieval is still hybrid dense + sparse with RRF.
On a box with Python 3.11/3.12 (or Docker), switch `EMBED_PROVIDER=bge_m3` and re-enable reranking
for the full-quality stack.

---

## Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_KEY` | — | **Required** for answer generation. Get one at console.groq.com. |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Generation model. |
| `QDRANT_URL` | `http://localhost:6333` | Compose overrides this to `http://qdrant:6333`. |
| `QDRANT_COLLECTION` | `qabuddy` | Collection name. |
| `EMBED_PROVIDER` | `bge_m3` | `bge_m3` \| `ollama` \| `hash` (see below). |
| `EMBED_MODEL` | `BAAI/bge-m3` | Embedding model id. |
| `RERANK_ENABLED` / `RERANKER_MODEL` | `true` / `BAAI/bge-reranker-v2-m3` | Cross-encoder rerank. |
| `TOP_K` / `RERANK_TOP_N` | `25` / `6` | Retrieve-then-rerank sizes. |
| `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN` / `JIRA_JQL` | — | Live JIRA REST fallback. |

> Secrets stay in `.env`, which is gitignored — nothing sensitive belongs in the repo.

### Embedding providers

- **`bge_m3`** (default) — `BAAI/bge-m3` via FlagEmbedding: 1024-d dense **and** native sparse
  lexical weights from one model. Best quality, needs torch (~4 GB with the reranker).
- **`ollama`** — local Ollama embeddings (dense only; sparse falls back to the built-in lexical
  encoder). Good for a machine without torch, e.g. `EMBED_MODEL=nomic-embed-text`.
- **`hash`** — deterministic, zero-dependency. **Smoke tests only; not for real answers.**

Switching the provider changes the dense dimension, so re-ingest into a fresh collection
(`--recreate`).

---

## Ingesting sources

Drop each source's data into its folder (`data/01_…` → `data/10_…`); each folder's `README.md`
lists exactly what it accepts. Then:

```bash
python -m qabuddy.cli ingest --source all        # everything
python -m qabuddy.cli ingest --source testcases  # one source
python -m qabuddy.cli ingest --source all --recreate   # drop + rebuild the collection
python -m qabuddy.cli stats                      # point count + embedder
python -m qabuddy.cli ask "Find the test case for submitting login with Enter"
```

| Source key | Folder | Adapter |
|---|---|---|
| `selenium` / `playwright` | `01`, `02` | shallow-clone + code-aware chunking (or use files you place there) |
| `testcases` | `03` | CSV/XLSX → one document per row |
| `jira` | `04` | JSON export, or live JQL via REST |
| `company_docs` | `05` | PDF/MD/DOCX/TXT prose chunks |
| `meeting_notes` | `07` | speaker-turn windows |
| `lucid_charts` | `08` | text/JSON diagram export |
| `prd` | `09` | PDF/MD/DOCX requirement docs |
| `jenkins` | `10` | log-aware chunks |

Figments of Phase 2 (**Figma**) live in `06_figma_designs` and are intentionally not ingested.

### JIRA

The build prompt calls for the **JIRA MCP connection + JQL**. Two paths are wired:

1. **Offline (works today):** export a JQL search response to `data/04_jira/*.json`.
2. **Live REST fallback:** set `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_JQL` in
   `.env` (same pattern as Chapters 3 and 7). One document is produced per ticket.

When you share the MCP configuration, point its issue export at `data/04_jira/` (or extend
`qabuddy/ingest/jira.py`) — no other part of the pipeline changes.

---

## Using the chatbot

Open **http://localhost:8501/** and ask, e.g.:

- *"Find the test case for submitting login with Enter"*
- *"What does the authentication-server-error test check?"*
- *"How do I create a new page object in the Selenium framework?"*

Each answer shows expandable **citation cards** (source file / test-case ID / JIRA key, snippet,
score). The sidebar filters by **source type** and **repo**; toggle **Show retrieved chunks** to
inspect the raw passages.

---

## Verifying

```bash
python -m unittest discover -s tests -v     # dependency-free pipeline tests
python scripts/eval_retrieval.py            # recall@1/5/10 + MRR
```

Expected sanity checks once the Chapter 11 CSV is ingested:

| Question | Expected top result |
|---|---|
| "Find the test case for submitting login with Enter" | `WING-LOGIN-TC-002` |
| "authentication server error test" | `WING-LOGIN-TC-089` |

An unsupported question must return *"Insufficient evidence in the knowledge base."*

---

## Deploying to a droplet (24x7)

```bash
# on the Ubuntu droplet
curl -fsSL https://get.docker.com | sh
git clone <your-repo> && cd Chapter_12_RAG_QA_BuddyAI
nano .env                                # set GROQ_KEY (+ optional JIRA_*)
docker compose up -d --build
docker compose run --rm app python -m qabuddy.cli ingest --source all
```

Put **Caddy** or nginx in front for TLS and expose 80/443, and remove the `127.0.0.1:` prefix on
the app port mapping so the reverse proxy can reach it. Restrict ingress so the bot stays internal.

**Sizing (honest):** bge-m3 (~2.3 GB) + reranker (~2.2 GB) fit comfortably on **4 GB RAM / 2 vCPU**
(~$24/mo DO). Cost-first alternative: `EMBED_PROVIDER=ollama` with `nomic-embed-text` and
`RERANK_ENABLED=false` on **2 GB**. Models cache in the `model_cache` volume, so restarts don't
re-download. Free 24x7 options: Oracle Cloud Always Free, or run locally.

---

## Project layout

```
Chapter_12_RAG_QA_BuddyAI/
├─ app.py                 Streamlit chatbot
├─ qabuddy/               config, embeddings, sparse, qdrant_store, chunking,
│                         ingest/*, retrieval, rag, cli
├─ scripts/               ingest_all.py, eval_retrieval.py
├─ tests/                 dependency-free pipeline tests
├─ data/01..10/           source folders (each with its own README)
├─ docker-compose.yml · Dockerfile · requirements.txt
└─ plan.md · prompt.md · README.md
```

---

## Phase 2 (documented, not built)

- **Hourly auto-ingestion:** a scheduler diffs a manifest (file hashes / last commit SHA /
  JIRA `updated` JQL) and re-indexes only what changed. Deterministic point ids make it idempotent.
- **Figma ingestion** for ER diagrams, user guides, and wireframes.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Qdrant not reachable" in the sidebar | `docker compose up -d qdrant` |
| `Indexed chunks: 0` | Run an `ingest` command after placing data in `data/**`. |
| Generic/hallucinated answers | Confirm `GROQ_KEY` is set and retrieval returns citations. |
| Dimension mismatch error | You changed `EMBED_PROVIDER`; re-ingest with `--recreate`. |
| First query is slow | Models load on first use; subsequent queries are fast. |
