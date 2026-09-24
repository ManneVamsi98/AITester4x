# RAG, Embeddings & Vector Databases — The Complete Plain-English Guide (2026)

> One document that explains RAG end to end: **Ingestion → Retrieval → Augmentation → Generation**, plus embeddings and vector databases, what types exist, and which are free vs paid.
>
> Prices and benchmark scores are **snapshots from 2026** and change often. Always re-check the vendor's own pricing page before you build a budget. Nothing here is financial advice.

---

## Quick Answer Key (your 8 questions, one line each)

| # | Your question | One-line answer | Full detail |
|---|---|---|---|
| 1 | **What is RAG?** | Retrieval-Augmented Generation — a pattern where the AI *fetches* relevant data, *adds* it to the prompt, then *generates* an answer from it (open-book exam, not memorisation). | [§2](#2-what-is-rag) |
| 2 | **What is ingestion?** | The **offline** step that gets your data in: load → clean → **chunk** → embed → **index** into the vector DB. | [§4](#4-stage-1--ingestion) |
| 3 | **What is retrieval?** | The **online** step that finds the best-matching chunks for a question: embed the query → nearest-neighbour search → (optionally) rerank. | [§5](#5-stage-2--retrieval) |
| 4 | **What is augmentation?** | The **glue** step: assembling the retrieved chunks + the question + instructions into one prompt for the LLM. | [§6](#6-stage-3--augmentation) |
| 5 | **What is generation?** | The LLM writing the final answer **using only the supplied context**, ideally with citations and a "say I don't know" fallback. | [§7](#7-stage-4--generation) |
| 6 | **What is an embedding, and what is a vector database?** | An **embedding** is a list of numbers representing *meaning* (GPS coordinates for ideas). A **vector database** stores those vectors and finds the nearest ones fast. | [§11](#11-what-is-an-embedding) · [§19](#19-what-is-a-vector-database) |
| 7 | **How many types of embedding exist (free/paid)?** | ~**5 modality types** (text/image/multimodal/code/audio), ~**5 technique types** (dense/sparse/hybrid/multi-vector/binary), and **2 cost models** — free self-host vs paid API. In practice almost everyone uses dense text embeddings. | [§14](#14-how-many-types-of-embedding-exist) |
| 8 | **How many types of vector database exist (free/paid)?** | **5 architecture categories** — managed cloud, open-source self-hosted, existing-DB extension, embedded/local, serverless — across **30+ products** (≈14 shortlisted). Most are free to self-host; most also have a free managed tier. | [§21](#21-how-many-types-of-vector-database-exist) |

---

## Table of Contents

**Part 1 — RAG**
1. [The problem RAG solves (the open-book exam analogy)](#1-the-problem-rag-solves)
2. [What is RAG?](#2-what-is-rag)
3. [The whole pipeline at a glance](#3-the-whole-pipeline-at-a-glance)
4. [Stage 1 — Ingestion (the "I" nobody talks about)](#4-stage-1--ingestion)
5. [Stage 2 — Retrieval](#5-stage-2--retrieval)
6. [Stage 3 — Augmentation](#6-stage-3--augmentation)
7. [Stage 4 — Generation](#7-stage-4--generation)
8. [RAG vs Fine-Tuning](#8-rag-vs-fine-tuning)
9. [Naive RAG vs Advanced RAG (and the real accuracy gap)](#9-naive-rag-vs-advanced-rag)
10. [How RAG fails (and the fix for each)](#10-how-rag-fails)

**Part 2 — Embeddings**
11. [What is an embedding?](#11-what-is-an-embedding)
12. [How embeddings are made](#12-how-embeddings-are-made)
13. [Dimensions, distance metrics, and why they matter](#13-dimensions-and-distance-metrics)
14. [How many types of embedding exist?](#14-how-many-types-of-embedding-exist)
15. [Embedding models — Paid (API)](#15-embedding-models--paid-api)
16. [Embedding models — Free / Open Source](#16-embedding-models--free--open-source)
17. [How to choose an embedding model](#17-how-to-choose-an-embedding-model)
18. [Storage tricks: Matryoshka, quantization, binary embeddings](#18-storage-tricks)

**Part 3 — Vector Databases**
19. [What is a vector database?](#19-what-is-a-vector-database)
20. [How vector search actually works (indexes)](#20-how-vector-search-actually-works)
21. [How many types of vector database exist?](#21-how-many-types-of-vector-database-exist)
22. [Vector databases — full comparison table](#22-vector-databases--full-comparison)
23. [Free tiers vs paid, side by side](#23-free-tiers-vs-paid)
24. [Self-hosted vs managed cost](#24-self-hosted-vs-managed-cost)

**Part 4 — Putting it together**
25. [Pick a stack by budget and scale](#25-pick-a-stack-by-budget-and-scale)
26. [Cost cheat sheet with a worked example](#26-cost-cheat-sheet)
27. [Glossary](#27-glossary)
28. [Sources](#28-sources)

---

# Part 1 — RAG

## 1. The problem RAG solves

Imagine a very smart student who has read almost the entire internet — but **only up to a certain date**, and they have **no access to your company's private files**.

Ask that student *"What is our refund policy for the Pro plan?"* and one of three things happens:

1. They make up a confident-sounding but wrong answer → this is a **hallucination**.
2. They give you a generic, outdated answer.
3. They say *"I don't know"* — honest, but useless to you.

Large Language Models (LLMs) like GPT, Claude, and Gemini are exactly this student. They are great at **language** but blind to:

- **Private data** (your docs, tickets, contracts, wikis).
- **Fresh data** (anything after their training cutoff).
- **Specific data** (exact product codes, prices, policy clauses).

There are only two real fixes:

| Fix | What it is | Cost / effort |
|---|---|---|
| **Fine-tuning** | Retrain the model on your data so knowledge is baked into its weights | Expensive, slow, needs re-doing whenever data changes |
| **RAG** | Keep the data outside the model and **hand it to the model at question time** | Cheap, fast, updates instantly |

**RAG is the open-book exam.** Instead of forcing the student to memorise everything, you let them bring the textbook and look up the right page before answering. They still do the writing (generation) — they just get the facts from the book.

---

## 2. What is RAG?

**RAG = Retrieval-Augmented Generation.**

It is a design pattern (not a model, not a product) where an AI system:

1. **Stores** your knowledge in a searchable form.
2. **Searches** that store when a question arrives.
3. **Sticks** the best matches into the prompt.
4. **Asks** the LLM to answer *using only that context*.

Word by word:

| Piece | Meaning | Plain English |
|---|---|---|
| **Retrieval** | Fetch the most relevant chunks of your data | "Find the right pages" |
| **Augmented** | Add those chunks to the prompt | "Stick them in front of the question" |
| **Generation** | The LLM writes the answer from that context | "Write the answer from those pages" |

The LLM is no longer guessing from memory. It is **reading a cheat sheet you control** — so you get:

- ✅ Answers grounded in your real, current documents
- ✅ **Citations** (you can show which document the answer came from)
- ✅ Easy updates (change the document, not the model)
- ✅ Lower hallucination rate than a bare chatbot
- ✅ No need to retrain anything when data changes

---

## 3. The whole pipeline at a glance

RAG has **two phases** that people often blur together. The **offline** phase (ingestion) happens once when data changes; the **online** phase (retrieval → augmentation → generation) happens on every question.

```
========================= OFFLINE (once, or when data changes) =========================

  Your data                Chunking              Embedding            Vector DB
 (PDF, web, DB,  ────►   split into    ────►  turn each chunk  ────►  store vectors
  tickets, docs)          small pieces          into a vector          + metadata
     │                                                                     │
  1. INGEST     2. CHUNK       3. EMBED              4. INDEX  ◄────────────┘
                                                                      (index)


========================= ONLINE (every single question) ==============================

  User question ──► Embed question ──► Search vector DB ──► Top-K chunks
                                                                  │
                                                    5. RETRIEVE ◄─┘
                                                                  │
  Top-K chunks + question + instructions  ◄───────────────────────┘
                     │
              6. AUGMENT (build the prompt)
                     │
             LLM reads and answers
                     │
              7. GENERATE ──► Answer (+ citations)
```

The four stages the question asks about map onto this:

| Stage | When | What happens |
|---|---|---|
| **Ingestion** | Offline | Load → clean → chunk → embed → store |
| **Retrieval** | Online | Embed the query, search the store, get top matches |
| **Augmentation** | Online | Combine matches + question + instructions into one prompt |
| **Generation** | Online | The LLM writes the final answer |

---

## 4. Stage 1 — Ingestion

**Ingestion is the "get your data into the system" stage.** It is unglamorous, it is where most RAG projects actually fail, and practitioners consistently report spending **the majority of their build time here** — not on the fancy retrieval algorithms.

Ingestion itself has five sub-steps:

### 4.1 Loading (a.k.a. Extraction / "ETL")

Pull raw content from everywhere it lives:

- PDFs, Word docs, PowerPoint, Excel
- Web pages, Confluence/Notion, Google Drive
- Databases, CSV, JSON
- Support tickets, emails, Slack
- Images and scanned documents (need OCR first)

**Why it matters:** garbage in, garbage out. A PDF parsed badly (tables shredded, columns merged, headers lost) produces useless chunks no matter how good your model is.

### 4.2 Chunking (splitting)

You cannot feed a 200-page manual into the model or the vector store as one blob. You split it into **chunks** — the units that will be embedded, stored, and retrieved.

The chunk size is a **trade-off**:

| Chunk too small | Chunk too large |
|---|---|
| Loses surrounding meaning | Contains too many topics |
| "It was raised 3%." (3% of what?) | Dilutes the signal, wastes tokens |
| Precise match, useless context | Good context, imprecise match |

Common strategies:

| Strategy | How it works | Good for |
|---|---|---|
| **Fixed-size** | Split every N characters/tokens with overlap | Simple, fast baseline |
| **Recursive** | Split by paragraph → sentence → word until it fits | General purpose (most common default) |
| **Semantic** | Split where the meaning shifts (embedding-based) | Dense prose |
| **Document-aware** | Respect headings, sections, tables, code blocks | Structured docs, code |
| **Parent-child / sentence-window** | Index small unit, retrieve a larger parent/window | **Highest precision** — see advanced techniques |

Typical starting point: **~200–600 tokens per chunk with 10–20% overlap.**

### 4.3 Enrichment (metadata + context)

Attach useful fields to every chunk so you can later filter and trace it:

- `source`, `page`, `url`, `author`, `date`, `department`, `access_level`, `doc_type`

You can also prepend **context** to each chunk before embedding (e.g. *"This chunk is from the 2025 Refund Policy, section 3"*). This is called **Contextual Retrieval** and it cuts retrieval failures dramatically (see §9).

### 4.4 Embedding

Run each chunk through an **embedding model** to get a numeric vector (see [Part 2](#part-2--embeddings)). Same model must be used for your documents **and** your future queries — vectors from different models are not comparable.

### 4.5 Indexing (storing)

Write the vectors + metadata into a **vector database**, which builds a special index (HNSW, IVF, etc.) so searching millions of vectors takes milliseconds instead of seconds (see [Part 3](#part-3--vector-databases)).

**Ingestion summary:** *Load → Clean → Chunk → Enrich → Embed → Index.* Re-run it for changed documents (dedupe on a stable ID so re-runs don't create duplicates).

---

## 5. Stage 2 — Retrieval

**Retrieval is the moment of truth.** When a question arrives, retrieval finds the chunks that answer it. Everything downstream is only as good as what this step returns ("retrieval quality bounds answer quality").

### 5.1 The basic flow

1. **Embed the query** with the *same* model used at ingestion.
2. **Search** the vector store for the nearest vectors (the "Top-K" closest chunks).
3. **(Optional) Rerank** the candidates with a more accurate model.
4. **(Optional) Filter** by metadata (e.g. only `department = HR`, only `date > 2025`).
5. Return the final set of chunks.

### 5.2 The three retrieval "engines"

| Engine | How it matches | Strength | Weakness |
|---|---|---|---|
| **Dense (vector)** | Meaning / semantics | Paraphrases, synonyms, intent | Misses exact codes, names, rare terms |
| **Sparse (keyword)** e.g. BM25 | Exact words / term frequency | Exact IDs, SKUs, acronyms, names | Misses paraphrases |
| **Hybrid** | Both, merged (usually via **RRF**) | Best of both — **production default** | Slightly more setup |

> **Hybrid search** (dense + sparse merged with Reciprocal Rank Fusion) is considered the highest-ROI upgrade to any RAG system in 2026. Dense alone will happily miss the exact phrase `"ERROR-4471"`.

### 5.3 Why "similar" means "close" (the intuition)

Every chunk becomes a point in a high-dimensional space. A question becomes a point too. Retrieval finds the **nearest points** to the query point. "Nearest" is measured by a distance metric — usually **cosine similarity** (angle between vectors) or **dot product**.

### 5.4 Top-K

- **K too small** → you might miss the answer.
- **K too large** → extra noise, more tokens, slower, and the LLM may get distracted ("lost in the middle").

Typical: retrieve **K = 20–50** candidates, then rerank down to **3–10** to actually feed the LLM.

---

## 6. Stage 3 — Augmentation

**Augmentation is the "glue" step** — assembling the final prompt that the LLM will see. It is mostly prompt engineering plus context management, but it is where a lot of answer quality is won or lost.

A typical augmented prompt:

```
SYSTEM:
You are a support assistant. Answer ONLY using the context below.
If the answer is not in the context, say "I don't know."
Always cite the source file name.

CONTEXT:
[1] (refund_policy_2025.pdf, p.4)
    Pro plan customers may request a full refund within 30 days...
[2] (billing_faq.md)
    Refunds are processed to the original payment method within 5-7 days...

USER QUESTION:
Can I get my money back for the Pro plan?
```

Key augmentation decisions:

| Decision | Why it matters |
|---|---|
| **How many chunks** to include | Too few = missing facts; too many = noise + cost |
| **Ordering** | Models pay most attention to the beginning and end ("lost in the middle") |
| **Instructions** | "Use only this context", "cite sources", "say I don't know if absent" |
| **Deduplication / compression** | Remove overlapping or irrelevant text to save tokens |
| **Citations** | Include chunk IDs/sources so the answer can be traced |

That is literally what "**augmented**" means: the question is *augmented* with retrieved context before generation.

---

## 7. Stage 4 — Generation

**The LLM writes the answer** using the augmented prompt. It is now behaving like an open-book student: reading the provided passages and composing a response.

What good generation looks like:

- **Grounded** — every claim traceable to a provided chunk.
- **Cited** — names the sources.
- **Honest** — says "I don't know" when the context lacks the answer (this is the single best anti-hallucination guardrail).
- **Concise** — answers the question, doesn't dump the whole context.

Important truths:

- The LLM **cannot** reliably "fact-check" fiction. If retrieval gave it wrong/no context, generation will often still sound confident. **Fixing retrieval fixes the answer.**
- Generation models are swappable — the same RAG pipeline can feed GPT, Claude, Gemini, or a local model. RAG is **model-agnostic**.

---

## 8. RAG vs Fine-Tuning

They solve different problems and are **complementary**, not competitors.

| Question | **RAG** | **Fine-tuning** |
|---|---|---|
| Where does knowledge live? | Outside the model (retrievable store) | Inside the model (weights) |
| Best for | Facts, docs, fresh/changing data, citations | Style, tone, format, narrow skills, domain jargon |
| Update cost | Re-ingest a document (minutes) | Retrain (expensive, slow) |
| Hallucination control | Strong (grounded + citations) | Weak (can't cite) |
| Data volume needed | Any amount works | Usually need many good examples |
| Cost profile | Cheap to start | Expensive to train, cheap to run |
| Transparency | High (you can show sources) | Low ("the model just knows") |

**Rule of thumb:** use **RAG for knowledge** ("what is true") and **fine-tuning for behaviour** ("how to answer"). Many production systems use **both**: fine-tune for tone/format, RAG for facts.

---

## 9. Naive RAG vs Advanced RAG

**Naive RAG** = chunk → embed → top-K cosine search → stuff into prompt → generate. Easy to build, and it hits a hard accuracy ceiling.

The **CRAG benchmark (2024)** put real numbers on that ceiling:

| System | Factual questions answered with **no hallucination** |
|---|---|
| LLM with no retrieval | ~34% |
| **Naive RAG** (straightforward retrieval) | **44%** |
| **State-of-the-art industry RAG** (advanced techniques) | **63%** |

So advanced techniques are worth roughly **+19 points of factual accuracy** over naive RAG — and naive RAG is worth far more than nothing.

### The 12 proven advanced techniques

| # | Technique | What it does | Best for | Reported gain | Complexity |
|---|---|---|---|---|---|
| 1 | **Hybrid Retrieval** | Dense + sparse (BM25) merged with RRF | Production default | De facto standard | Medium |
| 2 | **Cross-Encoder Reranking** | Second-pass model scores each (query, doc) pair | Precision-critical | Consistent NDCG/MRR lift | Low–Med |
| 3 | **Contextual Retrieval** | LLM prepends chunk context before embedding | Chunks losing meaning in isolation | **67% fewer** retrieval failures (Anthropic) | Medium |
| 4 | **HyDE** | Generate a hypothetical answer, embed *that* | Short/vague queries vs technical docs | nDCG@10 **61.3 vs 44.5** | Low–Med |
| 5 | **Self-RAG** | Model decides *when* to retrieve + critiques output | Factuality, citation accuracy | Beats standard RAG on open QA | High |
| 6 | **CRAG** | Evaluator grades retrieved docs; web fallback | Legal/medical/compliance | Significant over RAG | Medium |
| 7 | **Adaptive RAG** | Classifier routes query to no/single/multi-step | Mixed-complexity workloads | Efficiency + accuracy | Medium |
| 8 | **GraphRAG** | Knowledge graph + community summaries | Multi-hop relationship queries | "Substantial" (Microsoft) | High |
| 9 | **RAPTOR** | Recursive summary tree, multi-level retrieval | Long docs, cross-section reasoning | **+20%** on QuALITY | High |
| 10 | **RAG Fusion** | Multi-query generation + RRF merge | Ambiguous, recall-first | Broader coverage | Low–Med |
| 11 | **Sentence Window / Parent-Child** | Index small, retrieve larger window/parent | Chunking is the bottleneck | **#1 precision** in ARAGOG | Low–Med |
| 12 | **Modular RAG** | Swappable pipeline modules | Systems that will evolve | Architecture-level | Med–High |

**Highest-ROI starting point for most teams:** **Hybrid Retrieval + Sentence-Window Chunking**, then **Contextual Retrieval**, then **Reranking**.

> ⚠️ Nuance: not every "upgrade" helps everywhere. In the ARAGOG benchmark, Cohere Rerank showed **no advantage over naive RAG** on that corpus, while LLM-based reranking did help. **Always benchmark on your own data** before assuming a technique will help.

---

## 10. How RAG fails

Naive RAG fails in predictable ways. Diagnose **where** the pipeline breaks before reaching for a fancy fix.

| Failure | Symptom | Typical fix |
|---|---|---|
| **Bad ingestion** | PDFs/tables mangled | Better parsers, OCR, cleanup |
| **Bad chunking** | Answers cut mid-thought or diluted | Semantic / sentence-window / parent-child chunking |
| **Missing exact match** | Wrong answer for codes, SKUs, names | **Hybrid search** (add sparse/BM25) |
| **Low precision** | Right area, wrong chunk | **Reranking** |
| **Chunks lack context** | Ambiguous pronoun "it" in chunk | **Contextual Retrieval** |
| **Wrong vocabulary** | Vague query vs technical doc | **HyDE**, query rewriting |
| **Answer not in top-K** | Retrieval simply missed it | Bigger K, better embeddings, hybrid |
| **LLM ignores context** | Makes things up anyway | Stronger instructions, citation forcing, "say I don't know" |
| **Stale data** | Old info | Re-ingest; freshness filters |

**Golden rule:** *most RAG failures are retrieval failures, not model failures.* Fix the input before blaming the LLM.

---

# Part 2 — Embeddings

## 11. What is an embedding?

**An embedding is a list of numbers that represents the meaning of something.**

Example (massively simplified — real ones have hundreds/thousands of numbers):

```
"dog"    → [ 0.91, -0.14,  0.55, ... ]
"puppy"  → [ 0.89, -0.11,  0.52, ... ]   ← very close to "dog"
"car"    → [-0.32,  0.77, -0.09, ... ]   ← far from "dog"
```

**The GPS analogy:** an embedding is like a set of GPS coordinates — but for *meaning* instead of geography. Things that mean similar things end up at nearby coordinates; things that mean different things end up far apart.

This is why RAG works: `"help me get my money back"` lands **near** `"refund policy"` even though they share **zero keywords**. Keyword search can't do this. Embeddings can.

Where embeddings are used:

- **RAG** (the focus here)
- Semantic search
- Recommendations ("similar items")
- Clustering / topic discovery
- Deduplication
- Classification
- Anomaly detection

---

## 12. How embeddings are made

An embedding model (a neural network, usually a Transformer) is trained so that:

- **Semantically similar** texts → vectors that are **close**
- **Semantically different** texts → vectors that are **far**

Training typically uses **contrastive learning**: show the model pairs that *should* be close (a question and its answer) and pairs that *shouldn't* (unrelated), and nudge the vectors accordingly over millions of examples. Retrieval-focused models are trained specifically on **query–document** pairs, which is why a model can score well on the overall MTEB benchmark yet be only average at retrieval — and vice-versa (always look at the **MTEB-Retrieval** column for RAG).

**Key consequence:** vectors are only comparable **within the same model**. Change the model → every stored vector must be **re-embedded**. Models are not interchangeable mid-stream.

---

## 13. Dimensions and distance metrics

### Dimensions

The "dimension" is how many numbers are in each vector. More dimensions *can* capture more nuance, but with **diminishing returns** and real costs:

| Dimension | Storage per vector (float32) | Notes |
|---|---|---|
| 384 | ~1.5 KB | Small, fast, lower quality |
| 768 | ~3 KB | Good balance |
| 1024 | ~4 KB | Common sweet spot |
| 1536 | ~6 KB | OpenAI small |
| 3072 | ~12 KB | OpenAI large — ~4× the storage for marginal gains |

Higher dimensions = **more storage, slower search, more RAM**. For most RAG apps, **768–1536** is plenty. Some models support **Matryoshka** truncation (see §18) so you can pick a smaller size from a big model.

### Distance metrics

| Metric | Measures | Typically used by |
|---|---|---|
| **Cosine similarity** | Angle between vectors (ignores length) | Most text embeddings (default choice) |
| **Dot product** | Angle + magnitude | OpenAI embeddings, many models |
| **Euclidean (L2)** | Straight-line distance | Some image/vision models |

Most modern text embeddings are **normalised**, which makes cosine and dot product equivalent — you usually don't need to decide; the model's docs tell you which to use.

---

## 14. How many types of embedding exist?

There is no single official count, because "type" can mean several different things. Here are the **four useful ways to slice them** — and roughly how many exist in each:

### A. By modality (what is being embedded) — ~5 families

| Type | Embeds | Example models |
|---|---|---|
| **Text** | Words, sentences, documents | OpenAI text-embedding-3, BGE-M3, Nomic |
| **Image** | Pictures | CLIP, SigLIP |
| **Multimodal / cross-modal** | Text **and** images in one space | Cohere Embed v4, Gemini Embedding, CLIP |
| **Code** | Source code | Voyage-code-3, code-specific models |
| **Audio / Video** | Sound, video | CLAP, video encoders (niche) |

### B. By technique (how the vector is built) — ~5 families

| Type | What it is | Note |
|---|---|---|
| **Dense** | One vector per text; captures meaning | The standard RAG embedding |
| **Sparse** | Mostly-zero vector of term weights | BM25, SPLADE — powers keyword/hybrid |
| **Hybrid / multi-functional** | One model emits dense + sparse + multi-vector | e.g. BGE-M3 |
| **Multi-vector (late interaction)** | Many vectors per doc | ColBERT — more accurate, more storage |
| **Binary / quantised** | 0/1 or low-bit vectors | ~32× smaller, tiny accuracy loss |

### C. By domain specialisation — 2 groups

- **General-purpose** (web/news/general text)
- **Domain-specific** (code, legal, finance, medical, multilingual) — can beat general models by 5–10 points on the right corpus

### D. By **free vs paid** (deployment/licensing) — 2 groups

- **Free / open-source** — download the weights, self-host, pay only for compute
- **Paid / proprietary API** — pay per token, no infrastructure

**Plain answer:** there are roughly **5 modality types**, **5 technique types**, and **2 cost models** (free self-host vs paid API). In practice, **the vast majority of RAG systems use dense text embeddings**, choosing between a **free open-source model** and a **paid API**.

---

## 15. Embedding models — Paid (API)

All prices are **USD per 1M input tokens**, a 2026 snapshot. Embeddings bill **input only** — there is no output charge (the output is a fixed-size vector, not generated text).

| Model | Provider | Price /1M | Dimensions | Max input | Notes |
|---|---|---:|---:|---:|---|
| **text-embedding-3-small** | OpenAI | **$0.020** | 1536 (shortenable) | 8K | Best cheap default; $0.01 batch |
| **Jina Embeddings v3** | Jina AI | **$0.020** | 1024 | 8K | Multilingual; CC BY-NC for self-host |
| **Voyage-3.5** | Voyage AI (MongoDB) | $0.060 | 1024 | 32K | Strong quality-per-dollar |
| **Mistral Embed** | Mistral | $0.100 | 1024 | 8K | Solid multilingual |
| **Cohere Embed v4** | Cohere | $0.120 | 1536 (Matryoshka) | **128K** | Multimodal, 100+ languages |
| **text-embedding-3-large** | OpenAI | $0.130 | 3072 (shortenable) | 8K | Highest-quality OpenAI; $0.065 batch |
| **Gemini Embedding** | Google | $0.150 | 3072 (Matryoshka) | 2K | Multimodal |
| **voyage-3-large** | Voyage AI | ~$0.180 | 2048 | 32K | **Top API retrieval quality** |
| **voyage-code-3 / -law-2 / -finance-2** | Voyage AI | varies | — | — | Domain-specialised |

### MTEB leaderboard snapshot (2026) — sort by retrieval, not average

For RAG, the **MTEB-Retrieval** column predicts real-world quality better than the overall average.

| Model | Type | MTEB avg | **MTEB-Retrieval** | Dims | License |
|---|---|---:|---:|---:|---|
| **NV-Embed-v2** | NVIDIA | ~72.3 | ~61 | 4096 | Apache 2.0 (self-host) |
| **voyage-3-large** | Voyage AI | ~70.1 | **~62–63** | 2048 | Proprietary (API) |
| **gte-Qwen2-7B-instruct** | Alibaba/BAAI | ~69.5 | ~59 | 3584 | Apache 2.0 |
| **Cohere embed-v4** | Cohere | ~68.2 | ~60–61 | 256–1536 (MRL) | Proprietary (API) |
| **bge-multilingual-gemma2** | BAAI | ~67.4 | ~56 | 3584 | Apache 2.0 |
| **voyage-3** | Voyage AI | ~66.5 | ~57 | 1024 | Proprietary (API) |
| **mxbai-embed-large-v1** | MixedBread | ~65.3 | ~55 | 1024 | Apache 2.0 |
| **text-embedding-3-large** | OpenAI | ~64.6 | ~58–59 | 3072 | Proprietary (API) |
| **jina-embeddings-v3** | Jina AI | ~64.1 | ~54 | 1024 | CC BY-NC 4.0 |
| **text-embedding-3-small** | OpenAI | ~62.3 | ~55 | 1536 | Proprietary (API) |

> Scores are **approximations** from the public MTEB v2 leaderboard and shift constantly. Verify at `huggingface.co/spaces/mteb/leaderboard`.

**Notable:** `voyage-3-large` ranks *second* on the overall average but *first* on retrieval — exactly why RAG teams should sort by the retrieval column. And `text-embedding-3-large` (8th overall) closes much of the gap on retrieval.

---

## 16. Embedding models — Free / Open Source

These are **free to download and self-host**. You pay only for the compute (CPU is fine for small volume; a GPU for large volume). Run them with **sentence-transformers**, **Ollama**, **Hugging Face**, **vLLM**, etc.

| Model | Dims | Max tokens | MTEB avg | Size | License | Best for |
|---|---:|---:|---:|---:|---|---|
| **all-MiniLM-L6-v2** | 384 | 512 | ~56 | ~90 MB | Apache 2.0 | Speed; massive batch, CPU-only |
| **all-mpnet-base-v2** | 768 | 512 | ~57.8 | ~420 MB | Apache 2.0 | Higher quality than MiniLM |
| **nomic-embed-text-v1.5** | 768 | 8K | ~62.4 | ~550 MB | Apache 2.0 | Best small English model; open training data |
| **BAAI/bge-m3** | 1024 | 8K | ~62.6 | ~2.3 GB | MIT | **Best all-round free pick**; multilingual; dense+sparse+multi-vector |
| **Qwen3-Embedding** | 1024–4096 | 32K | top-tier | large | Apache 2.0 | Max quality if you have the GPU |
| **NV-Embed-v2** | 4096 | 32K | ~72.3 | 7.8B params | Apache 2.0 | Benchmark leader (needs A100-class GPU) |
| **gte-Qwen2-7B-instruct** | 3584 | 32K | ~69.5 | 7B params | Apache 2.0 | High quality, multilingual |
| **mxbai-embed-large-v1** | 1024 | 512 | ~65.3 | ~670 MB | Apache 2.0 | Strong quality, short inputs |
| **E5 family** (e.g. e5-large) | 1024 | 512 | high | varies | MIT | Well-rounded, widely used |

**When free/open-source wins:**

- ✅ High volume (per-token API costs add up fast)
- ✅ Multilingual needs (BGE-M3 is excellent)
- ✅ **Data privacy** — nothing leaves your infra
- ✅ No rate limits; full control; fine-tune on your data
- ✅ You already have GPUs

**When paid API wins:**

- ✅ Low volume (< ~10M tokens/month → API is cheaper than a GPU)
- ✅ Zero ops / no infrastructure management
- ✅ You want the latest model without evaluating/deploying it yourself
- ✅ Predictable latency and uptime

---

## 17. How to choose an embedding model

1. **Sort by MTEB-Retrieval**, not the overall average.
2. **Check for a domain variant** (code → `voyage-code-3`; legal → `voyage-law-2`; finance → `voyage-finance-2`).
3. **Do the cost math** at your monthly token volume (see §26).
4. **Benchmark on your own data.** Build a held-out set of **100–500 query→correct-document pairs** from your real corpus (include "hard negatives"). Compute **recall@5, recall@10, and MRR** for each candidate. This is the single highest-value step and beats any public leaderboard.
5. **Re-check monthly.** The open-source tier moves fast — upgrade when a new model beats yours by **3+ points** on retrieval.

**Quick defaults:**

| Situation | Pick |
|---|---|
| Cheapest good paid default | `text-embedding-3-small` ($0.02) |
| Best API retrieval | `voyage-3-large` |
| Best all-round free | `BAAI/bge-m3` |
| Free + tiny/fast | `all-MiniLM-L6-v2` |
| Multilingual | `bge-m3` or Cohere `embed-v4` |
| Long documents (no chunking) | Cohere `embed-v4` (128K context) |

---

## 18. Storage tricks

Since storage cost scales with **dimensions × number of vectors**, these tricks matter:

| Trick | How | Effect |
|---|---|---|
| **Matryoshka (MRL)** | Train so the first N dims are usable alone → truncate 3072→1024/768/512 | Keeps quality model, stores smaller vectors |
| **Quantization** | Store as int8 / int4 instead of float32 | **2–4× less storage**, small quality loss |
| **Binary embeddings** | Store as 0/1 bits | Up to **~32× smaller**; tiny accuracy loss |
| **Dimension choice** | Pick 768–1024 instead of 3072 | 2–4× less storage for marginal quality difference |

---

# Part 3 — Vector Databases

## 19. What is a vector database?

**A vector database stores vectors and finds the nearest ones fast.**

**The library analogy:** a normal database is a card catalogue that finds books by **exact title**. A vector database is a librarian who finds books by **what you mean** — "something about losing a job" → the shelf on career transitions.

Formally, it stores:

- the **vector** (for similarity search),
- the **original content / chunk text** (to feed the LLM),
- the **metadata** (for filtering: source, date, permissions...).

...and answers the query: *"give me the K vectors nearest to this query vector."*

### Why not just use a normal database?

Normal databases (and SQL `LIKE`, Elasticsearch keyword search) match **exact or near-exact terms**. They cannot answer "find the closest point in 1024-dimensional space, meaning-wise." That is a different kind of operation, and it needs a different index.

### Vector DB vs vector *library*

| | Vector **library** (e.g. FAISS) | Vector **database** |
|---|---|---|
| Stores vectors + search | ✅ | ✅ |
| Persistence, CRUD, updates | ❌ | ✅ |
| Metadata filtering | Limited | ✅ |
| Users, auth, backups, scaling | ❌ | ✅ |
| Best for | Local experiments, embedded use | Production systems |

FAISS (Meta) is a **library**, not a database. Chroma and LanceDB are "embedded" databases. Pinecone/Qdrant/Weaviate/Milvus are full databases.

---

## 20. How vector search actually works

### Brute force is too slow

Comparing a query against every vector (**exact / flat** search) is 100% accurate but **O(n)** — fine for 10K vectors, painful for 100M.

### Approximate Nearest Neighbour (ANN)

ANN indexes trade a *tiny* bit of accuracy (recall) for **massive** speed gains. The main index types:

| Index | Idea | Notes |
|---|---|---|
| **HNSW** | Navigable "small-world" graph; hop toward the query | **Most common default.** Fast, high recall; RAM-hungry |
| **IVF** | Cluster vectors, search only nearby clusters | Less memory; tune `nprobe` for speed/accuracy |
| **IVF + PQ** | Clusters + product quantisation (compress vectors) | Huge datasets on limited RAM |
| **DiskANN / Disk-based** | Graph on SSD instead of RAM | Billions of vectors cheaply |
| **Flat / brute force** | Compare everything | Small datasets, maximum accuracy |

### The typical search call

1. (Optional) **Filter** by metadata (e.g. `access_level = public`).
2. **ANN search** for the top candidates using HNSW/IVF.
3. Return top-K with distances + metadata.

### Hybrid search inside the DB

Many vector DBs now do **hybrid** (dense + sparse) natively and merge with RRF — so you don't need a separate keyword engine.

---

## 21. How many types of vector database exist?

Vector databases come in **5 architecture categories**, plus dozens of individual products. Because "type" is ambiguous, here's the full picture:

| # | Category | What it is | Examples | Free? |
|---|---|---|---|---|
| 1 | **Managed cloud (dedicated)** | Vendor-hosted, zero ops, purpose-built | Pinecone, Zilliz Cloud, Weaviate Cloud, Qdrant Cloud | Free tier + paid |
| 2 | **Open-source self-hosted** | Run it yourself, no feature gating | Qdrant, Milvus, Weaviate, Chroma, LanceDB, Vald | **Free** (you pay for infra) |
| 3 | **Vector extension for an existing DB** | Add vector search to a database you already run | pgvector (Postgres/Supabase/Neon), MongoDB Atlas Vector Search | Free tier + paid |
| 4 | **Embedded / local (library-style)** | Runs in-process with your app, no server | Chroma, LanceDB, FAISS | **Free** |
| 5 | **Serverless / pay-per-use** | HTTP API, edge-friendly, no connections | Upstash Vector, Turbopuffer, Cloudflare Vectorize | Free tier + paid |

**Counts:** ~**5 categories**, **30+ real products** on the market, and about **14 worth shortlisting** for a typical RAG stack (listed in the next section). In 2026 most tracked tools offer a free tier, and Qdrant, Milvus, Chroma, and LanceDB are **fully free to self-host with no limits**.

---

## 22. Vector databases — full comparison

| Product | Category | Hosting | Open source | Hybrid search | Notes |
|---|---|---|---|---|---|
| **Pinecone** | Managed | Cloud | ❌ | ✅ | Largest ecosystem, simplest API |
| **Qdrant** | Managed + OSS | Cloud/self | ✅ | ✅ | Rust, fast, great free tier |
| **Weaviate** | Managed + OSS | Cloud/self | ✅ | ✅ | Multi-modal, generative search |
| **Milvus** | OSS (+ Zilliz Cloud) | self/cloud | ✅ | ✅ | Enterprise scale, GPU-accelerated |
| **Zilliz Cloud** | Managed (Milvus) | Cloud | (Milvus is OSS) | ✅ | Managed Milvus, generous free tier |
| **Chroma** | Embedded/OSS | Local/self | ✅ | Basic | Python-native, simplest to start |
| **LanceDB** | Embedded | Local/cloud storage | ✅ | ✅ | Zero-copy, multimodal, serverless-friendly |
| **pgvector** | Postgres extension | Self | ✅ | Manual | Vectors in plain SQL — no new infra |
| **Supabase / Neon pgvector** | Postgres + pgvector | Cloud | (pgvector OSS) | Manual | Vectors alongside relational data |
| **MongoDB Atlas Vector Search** | Document DB + vector | Cloud | ❌ | ✅ | Combine with aggregation pipeline |
| **Redis Vector** | In-memory + vector | Self/cloud | ✅ | ✅ | Very low latency |
| **Upstash Vector** | Serverless | Cloud | ❌ | ✅ | REST API, edge/serverless |
| **Turbopuffer** | Serverless (S3-backed) | Cloud | ❌ | ✅ | Cheap storage, pay-per-use |
| **Marqo, Vald, Cloudflare Vectorize** | Various | Various | mixed | varies | Niche / specialised |

**Index types supported:** almost all support **HNSW**; Milvus/Qdrant/Pinecone add IVF/DiskANN variants; several add quantisation and metadata filtering.

---

## 23. Free tiers vs paid

Snapshot from vendor pricing pages (2026). Free tiers change frequently.

| Product | Free tier | Paid from | Model |
|---|---|---|---|
| **Pinecone** | ~1M vectors / 2 GB, 2M writes, 1M reads, 5M embed tokens | ~$20–50/mo | Usage-based |
| **Qdrant Cloud** | 1 GB free cluster (forever) | ~$10/mo | Per-cluster |
| **Weaviate Cloud** | **Permanent free**: 100K objects, 1 GB mem, 10 GB disk, 1 collection | $45/mo (Flex) | Per-cluster + dimensions |
| **Zilliz Cloud** | 5 GB / ~5M vectors, 5 collections | ~$65/mo | Compute units |
| **Chroma** | Unlimited (self-host) | Cloud usage-based | Self-host free |
| **LanceDB** | Unlimited (OSS) | Cloud after $100 credits | Self-host free |
| **Upstash Vector** | Free: **10K queries/day** (200M vector-dim capacity, 1 GB data, max 1536 dims) | $0.40 / 100K requests | Per-query + per-vector |
| **Turbopuffer** | No free tier | ~$0.30/M vectors/mo stored | Pay-per-use |
| **Supabase pgvector** | 500 MB shared, included | $25/mo Pro | Per-project |
| **Neon pgvector** | 512 MB/project, 100 projects | $19/mo | Usage-based |
| **MongoDB Atlas Vector** | 512 MB (M0, always free) | ~$57/mo (M10) | Per-cluster |

**Best free tier (managed):** Zilliz Cloud (5 GB) or Pinecone (~1M vectors).
**Best free (self-host, unlimited):** Qdrant, Milvus, Chroma, LanceDB.
**Easiest zero-infra start:** Supabase/Neon pgvector or MongoDB Atlas free.

> ⚠️ **Hidden costs** beyond the DB: **embedding API spend**, **dimension size** (3072 dims ≈ 4× the storage of 768), **index build time/RAM** (HNSW needs ~2–4× the vector data in RAM), **query latency** under load, and **vendor lock-in** (proprietary DBs may not offer a portable export). Open-source and pgvector keep you portable.

---

## 24. Self-hosted vs managed cost

Illustrative monthly costs for 1M and 10M vectors:

| Approach | 1M vectors | 10M vectors | Ops burden | Best for |
|---|---|---|---|---|
| Qdrant self-hosted | $5–10 (VPS) | $20–50 | Medium | Cost-sensitive teams |
| Chroma self-hosted | $5–10 | $20–40 | Low | Prototypes, small/medium RAG |
| pgvector (self-hosted PG) | $5–15 | $30–80 | Medium | Teams already on Postgres |
| Milvus self-hosted | $15–30 | $50–100 | **High** | Large scale, dedicated infra |
| Pinecone (managed) | $0 (free tier) | $70–200 | None | Zero-ops |
| Qdrant Cloud | $0 (free tier) | $30–100 | None | Easy start w/ OSS escape hatch |
| Zilliz Cloud | $0 (free tier) | $65–200 | None | Managed Milvus |

**Bottom line:** managed services cost ~2–5× more but remove all ops. **Start on a free managed tier → move to self-hosted when cost matters and you have ops capacity.**

---

# Part 4 — Putting it together

## 25. Pick a stack by budget and scale

| Your situation | Embedding | Vector DB | LLM |
|---|---|---|---|
| **Learning / prototype (free)** | BGE-M3 or all-MiniLM (local) | Chroma or pgvector (local) | Free/cheap LLM API |
| **Small production (cheap)** | text-embedding-3-small | Supabase/Neon pgvector or Qdrant free | Mid-tier LLM |
| **Serious production** | voyage-3-large or Cohere v4 | Qdrant Cloud / Pinecone / Zilliz | Top LLM |
| **High volume / cost-sensitive** | Self-host BGE-M3 | Self-host Qdrant/Milvus | Self-host or mixed |
| **Privacy / on-prem** | Self-host (BGE-M3, Qwen3) | Self-host Qdrant/Milvus | Self-host LLM |
| **Multilingual** | BGE-M3 or Cohere embed-v4 | Any | Any |
| **Multimodal (text+image)** | Cohere embed-v4 / CLIP | Weaviate (multi-modal) | Any |

**A solid, boring, works-in-production default:**

```
Hybrid retrieval (dense + BM25, RRF)
  + Sentence-window / parent-child chunking
  + Contextual Retrieval at index time
  + Cross-encoder reranking (top 20 → top 5)
  + Strong "answer only from context, cite sources, else say I don't know" prompt
```

---

## 26. Cost cheat sheet

### Embedding cost math

> Cost = **price per 1M tokens** × **total tokens**.
> Rough rule: **1 document ≈ 500 tokens**, so **1M documents ≈ 500M tokens**.

**Worked example — embedding 1 million documents (~500M tokens):**

| Model | Price /1M | Cost to embed 1M docs |
|---|---:|---:|
| BGE-M3 (self-host) | ~$0.010* | ~$5 (or just compute) |
| text-embedding-3-small | $0.020 | **~$10** |
| voyage-3.5 | $0.060 | ~$30 |
| Cohere embed-v4 | $0.120 | ~$60 |
| text-embedding-3-large | $0.130 | ~$65 |
| voyage-3-large | ~$0.180 | ~$90 |

*\*Open-weight models are free to self-host; the "price" reflects equivalent API/compute cost.*

**Plus storage:** 1M vectors at 1536 dims ≈ 6 GB raw (less with quantisation). Lower dimensions = cheaper storage. **Re-embedding is required whenever you change models** — budget for it.

### The honest production cost stack

```
Total RAG cost ≈ Embedding (one-time + re-embeds)
               + Vector DB (monthly)
               + LLM calls (per query, ongoing ← usually the biggest)
```

The LLM generation step usually dominates long-run cost, not embeddings or storage.

---

## 27. Glossary

| Term | Meaning |
|---|---|
| **RAG** | Retrieval-Augmented Generation — fetch relevant data, add to prompt, generate answer |
| **Chunk** | A small piece of a document that gets embedded and retrieved |
| **Embedding** | A vector of numbers representing meaning |
| **Vector** | An ordered list of numbers |
| **Dimension** | Length of a vector (e.g. 1536) |
| **Cosine similarity** | Angle-based similarity between vectors |
| **ANN / HNSW / IVF** | Approximate nearest-neighbour indexes for fast search |
| **Vector DB** | Database built for storing and searching vectors |
| **Top-K** | How many nearest results you retrieve |
| **Dense retrieval** | Meaning-based vector search |
| **Sparse retrieval** | Keyword/term-frequency search (BM25) |
| **Hybrid search** | Dense + sparse combined (often via RRF) |
| **RRF** | Reciprocal Rank Fusion — merges ranked lists |
| **Reranker** | Second-pass model that re-scores candidates for precision |
| **Cross-encoder** | Model that scores a (query, doc) pair together — accurate, slower |
| **Bi-encoder** | Model that embeds query and doc separately — fast, used for retrieval |
| **HyDE** | Generate a hypothetical answer and embed *that* to improve search |
| **GraphRAG** | RAG over a knowledge graph for multi-hop reasoning |
| **RAPTOR** | Recursive summary-tree indexing for long docs |
| **Self-RAG / CRAG / Adaptive RAG** | Self-critiquing / corrective / routing RAG variants |
| **Contextual Retrieval** | LLM-prepended context on each chunk before embedding |
| **Matryoshka (MRL)** | Truncatable embeddings — shrink dimensions, keep quality |
| **MTEB** | Massive Text Embedding Benchmark — public embedding leaderboard |
| **Recall@K** | Share of queries where the right doc is in the top K |
| **Hallucination** | Confident but fabricated output |
| **Grounding** | Tying answers to retrieved evidence |
| **pgvector** | Postgres extension for vector search |
| **ANN recall** | Accuracy of approximate search vs exact search |

---

## 28. Sources

**RAG fundamentals & pipeline**
- [Build AI Apps with RAG — Zilliz Learn](https://zilliz.com/learn/Retrieval-Augmented-Generation)
- [12 Advanced RAG Techniques Beyond Naive Retrieval — Atlan](https://atlan.com/know/advanced-rag-techniques/)
- [Production RAG in 2026: Hybrid Search, Reranking, GraphRAG — 1337skills](https://1337skills.com/blog/2026-06-12-production-rag-2026-hybrid-search-reranking-graphrag/)
- [What is Retrieval Augmented Generation Architecture — ProjectPro](https://www.projectpro.io/article/rag-architecture/1079)

**Advanced RAG research (cited benchmarks)**
- [Self-RAG, ICLR 2024](https://arxiv.org/abs/2310.11511) · [RAPTOR](https://arxiv.org/abs/2401.18059) · [HyDE](https://arxiv.org/abs/2212.10496) · [CRAG](https://arxiv.org/abs/2401.15884) · [GraphRAG (Microsoft)](https://arxiv.org/abs/2404.16130) · [Adaptive-RAG](https://arxiv.org/abs/2403.14403) · [RAG-Fusion](https://arxiv.org/abs/2402.03367) · [ARAGOG](https://arxiv.org/abs/2404.01037) · [CRAG benchmark](https://arxiv.org/abs/2406.04744) · [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

**Embeddings**
- [Embeddings API Pricing 2026 — AI API Prices](https://aiapiprices.com/embeddings-api-pricing/)
- [Embedding Model Leaderboard 2026: MTEB Rankings — AI Prompts Hub](https://aipromptshub.co/blog/embedding-model-leaderboard-2026)
- [Open Source Embedding Models: Which One to Use in 2026 — Pristren](https://pristren.com/blog/open-source-embedding-models/)
- [MTEB Leaderboard — Hugging Face](https://huggingface.co/spaces/mteb/leaderboard) · [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3)

**Vector databases**
- [Vector Database Pricing Comparison 2026 — AgentDeals](https://agentdeals.dev/vector-database-pricing)
- [Vector Database Pricing 2026: 14 Platforms — CostBench](https://costbench.com/software/vector-databases/)
- [Best Vector Databases 2026 — Toolradar](https://toolradar.com/blog/best-vector-databases)

**Benchmark numbers are approximations from public leaderboards as of 2026 and change continuously. Pricing comes from vendor pages and comparison sites as of 2026 — always confirm on the vendor's own pricing page before committing budget.**
