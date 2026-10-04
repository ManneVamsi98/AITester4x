"""Grounded, citation-forcing answer generation via Groq."""

from __future__ import annotations

from .retrieval import Retrieved

NO_EVIDENCE = "Insufficient evidence in the knowledge base."

SYSTEM_PROMPT = (
    "You are QABuddy, a QA knowledge assistant for an internal engineering team. "
    "Answer ONLY using the numbered context passages below. "
    "Every factual claim must cite its passage like [1] or [2]. "
    "Prefer quoting exact test-case IDs, JIRA keys, file paths, and steps. "
    "If the context does not contain the answer, reply exactly with: "
    f'"{NO_EVIDENCE}" '
    "Never use outside knowledge. Never invent IDs, paths, or steps."
)

MAX_CHARS_PER_PASSAGE = 4000


def _label(metadata: dict) -> str:
    parts = [
        metadata.get("source_file"),
        metadata.get("tc_id"),
        metadata.get("jira_key"),
        metadata.get("path"),
        metadata.get("repo"),
    ]
    return " · ".join(str(p) for p in parts if p)


def build_context(contexts: list[Retrieved]) -> str:
    blocks = []
    for number, item in enumerate(contexts, start=1):
        label = _label(item.metadata)
        text = item.text[:MAX_CHARS_PER_PASSAGE]
        blocks.append(f"[{number}] ({label})\n{text}")
    return "\n\n".join(blocks)


def generate(settings, question: str, contexts: list[Retrieved]) -> str:
    if not contexts:
        return NO_EVIDENCE
    if not settings.groq_key:
        return (
            "GROQ_KEY is not set, so I can't generate an answer. "
            "Add it to .env and restart. Retrieved sources are shown below."
        )

    from groq import Groq

    client = Groq(api_key=settings.groq_key)
    user_prompt = f"CONTEXT:\n{build_context(contexts)}\n\nQUESTION:\n{question}"
    completion = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (completion.choices[0].message.content or "").strip()
