// QABuddy.ai serverless API — Qdrant Cloud (hosted inference) + Groq, with a demo mode.
// Node runtime, no dependencies (uses the global fetch).

const DEMO = require("../demo-data");

const QDRANT_URL = (process.env.QDRANT_URL || "").replace(/\/+$/, "");
const QDRANT_API_KEY = process.env.QDRANT_API_KEY || "";
const COLLECTION = process.env.QDRANT_COLLECTION || "qabuddy";
const EMBED_MODEL = process.env.CLOUD_EMBED_MODEL || "sentence-transformers/all-MiniLM-L6-v2";
const GROQ_KEY = process.env.GROQ_KEY || "";
const GROQ_MODEL = process.env.GROQ_MODEL || "openai/gpt-oss-120b";
const TOP_K = Number(process.env.TOP_K || 8);
const MAX_PASSAGE_CHARS = 4000;

// Demo mode unless live credentials are present (DEMO_MODE=true/false overrides).
const FLAG = String(process.env.DEMO_MODE || "").toLowerCase();
const liveReady = Boolean(QDRANT_URL && QDRANT_API_KEY && GROQ_KEY);
const DEMO_MODE = FLAG === "true" || (FLAG !== "false" && !liveReady);

const NO_EVIDENCE = "Insufficient evidence in the knowledge base.";
const SYSTEM_PROMPT = [
  "You are QABuddy, a QA knowledge assistant for an internal engineering team.",
  "Answer ONLY using the numbered context passages below.",
  "Every factual claim must cite its passage like [1] or [2].",
  "Prefer quoting exact test-case IDs, JIRA keys, file paths, and steps.",
  `If the context does not contain the answer, reply exactly with: "${NO_EVIDENCE}"`,
  "Never use outside knowledge. Never invent IDs, paths, or steps.",
].join(" ");

function label(payload = {}) {
  return [payload.source_file, payload.tc_id, payload.jira_key, payload.path, payload.repo]
    .filter(Boolean)
    .join(" · ");
}

function buildFilter(sources) {
  if (!Array.isArray(sources) || sources.length === 0) return null;
  return { must: [{ key: "source_type", match: { any: sources } }] };
}

function demoReply(question) {
  const text = String(question).toLowerCase();
  let best = null;
  let bestScore = 0;
  for (const example of DEMO.examples) {
    const score = (example.keywords || []).reduce(
      (n, keyword) => n + (text.includes(keyword) ? 1 : 0),
      0
    );
    if (score > bestScore) {
      best = example;
      bestScore = score;
    }
  }
  if (best) {
    return { answer: best.answer, citations: best.citations, demo: true, matched: best.question };
  }
  return {
    answer: DEMO.intro,
    citations: [],
    demo: true,
    examples: DEMO.examples.map((e) => e.question),
  };
}

async function qdrantSearch(question, sources) {
  const base = { query: { text: question, model: EMBED_MODEL }, limit: TOP_K, with_payload: true };

  const attempt = async (body) => {
    const response = await fetch(`${QDRANT_URL}/collections/${COLLECTION}/points/query`, {
      method: "POST",
      headers: { "api-key": QDRANT_API_KEY, "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`Qdrant ${response.status}: ${(await response.text()).slice(0, 300)}`);
    }
    const data = await response.json();
    return (data.result && data.result.points) || [];
  };

  const filter = buildFilter(sources);
  if (filter) {
    try {
      return await attempt({ ...base, filter });
    } catch (_) {
      // A filtered field needs a payload index; fall back to an unfiltered search
      // rather than failing the whole request.
    }
  }
  return attempt(base);
}

async function groqAnswer(question, points) {
  const context = points
    .map(
      (p, i) =>
        `[${i + 1}] (${label(p.payload)})\n${(p.payload?.text || "").slice(0, MAX_PASSAGE_CHARS)}`
    )
    .join("\n\n");

  const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { authorization: `Bearer ${GROQ_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({
      model: GROQ_MODEL,
      temperature: 0.1,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: `CONTEXT:\n${context}\n\nQUESTION:\n${question}` },
      ],
    }),
  });
  if (!response.ok) {
    throw new Error(`Groq ${response.status}: ${(await response.text()).slice(0, 300)}`);
  }
  const data = await response.json();
  return (data.choices?.[0]?.message?.content || "").trim();
}

module.exports = async (req, res) => {
  // GET → lets the UI discover demo mode + example questions.
  if (req.method === "GET") {
    res.status(200).json({
      demo: DEMO_MODE,
      model: GROQ_MODEL,
      embedModel: EMBED_MODEL,
      examples: DEMO.examples.map((e) => e.question),
    });
    return;
  }
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const body = req.body || {};
  const question = String(body.question || "").trim();
  if (!question) {
    res.status(400).json({ error: "question is required" });
    return;
  }

  if (DEMO_MODE) {
    res.status(200).json(demoReply(question));
    return;
  }

  try {
    const points = await qdrantSearch(question, body.sources);
    const citations = points.map((p, i) => ({
      n: i + 1,
      source: label(p.payload),
      type: p.payload?.source_type || "",
      score: p.score,
      snippet: (p.payload?.text || "").slice(0, 400),
    }));

    if (points.length === 0) {
      res.status(200).json({ answer: NO_EVIDENCE, citations: [], demo: false });
      return;
    }

    const answer = await groqAnswer(question, points);
    res.status(200).json({ answer, citations, demo: false });
  } catch (error) {
    res.status(502).json({ error: String(error.message || error) });
  }
};
