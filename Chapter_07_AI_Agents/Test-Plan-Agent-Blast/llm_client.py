"""Groq LLM client for the Test Plan Agent.

Exactly one model call happens per plan: the agent sends the normalized
ticket payload and asks for a STRICT JSON test plan. The model never sees
the markdown template - render.py owns that.
"""

import json
import re

import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"  # verified working in Chapter 3
GROQ_TIMEOUT = 90

SYSTEM_PROMPT = (
    "You are a Senior QA Test Plan Architect. You produce STRICT JSON only - "
    "no markdown fences, no commentary, no trailing text. Every claim must be "
    "grounded in the ticket data you are given. If a fact is not present, put "
    "it in the 'assumptions' array with a note. Never invent URLs, dates, or tools."
)

USER_TEMPLATE = """Create a professional test plan for the Jira ticket below.

Return JSON with EXACTLY these keys:
- objective: string
- scope: array of objects {{ "entry": string, "justified_by": string }} (justified_by = the ticket fact that justifies this scope item)
- environments: array of strings
- test_cases: array of objects {{ "id": string, "title": string, "precondition": string, "steps": array of strings, "expected": string }}
- entry_criteria: array of strings
- exit_criteria: array of strings
- risks: array of objects {{ "risk": string, "mitigation": string }}
- deliverables: array of strings
- assumptions: array of strings

Rules:
- Derive scope entries ONLY from ticket facts; each must carry justified_by.
- Do not invent acceptance criteria, URLs, dates, or tool names.
- If the ticket is thin, note gaps in assumptions rather than inventing content.

TICKET (normalized):
{payload}
"""


class LLMError(Exception):
    """Raised when the Groq call fails or returns invalid JSON."""


def build_prompt(payload: dict) -> str:
    return USER_TEMPLATE.format(payload=json.dumps(payload, indent=2, ensure_ascii=False))


def _extract_json(text: str) -> dict:
    """Tolerate markdown fences or stray prose around the JSON object."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise LLMError("Groq response contained no JSON object.")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"Groq returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise LLMError("Groq JSON was not an object.")
    return data


def generate_plan_json(payload: dict, cfg: dict) -> dict:
    """Call Groq once and return the parsed test-plan JSON."""
    key = (cfg.get("groq_key") or "").strip()
    if not key:
        raise LLMError("Groq API key is not configured on the Settings screen.")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(payload)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(GROQ_URL, json=body, headers=headers, timeout=GROQ_TIMEOUT)
    except requests.RequestException as exc:
        raise LLMError(f"Could not reach Groq: {exc}") from exc
    if resp.status_code == 401:
        raise LLMError("Groq rejected the API key (401). Check the Settings screen.")
    if resp.status_code == 429:
        raise LLMError("Groq rate limited (429). Wait a moment and retry.")
    if resp.status_code >= 400:
        raise LLMError(f"Groq returned HTTP {resp.status_code}: {resp.text[:300]}")
    text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    if not text:
        raise LLMError("Groq returned an empty response.")
    return _extract_json(text)
