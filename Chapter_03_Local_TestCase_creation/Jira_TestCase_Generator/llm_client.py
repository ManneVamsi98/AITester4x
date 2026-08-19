"""LLM backend for the Jira Test Case Generator.

Default provider: Groq (groq.com) - Ollama is unreliable on this machine
(out-of-memory crashes), so it is used only when the user explicitly selects
it on the Settings screen.

No credentials are hardcoded here - the Groq key always comes from config.
"""

from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
# Preferred model per the spec; falls back to an installed small model if missing.
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_FALLBACK_MODELS = ("llama3.2:1b",)
# Fail fast - a dead/unusable Ollama should not stall the chat for minutes.
OLLAMA_TIMEOUT = 15
# Force CPU: GPU inference crashes with out-of-memory on this machine.
OLLAMA_OPTIONS = {"num_gpu": 0}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# Verified against the live Groq API (2026-08): llama-3.3-70b-versatile no longer exists.
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_TIMEOUT = 60

TEMPLATE_PATH = Path(__file__).parent / "templates" / "testcase_creator.md"


class LLMError(Exception):
    """Raised when every configured provider fails."""


def build_prompt(requirements_text: str, count: int) -> str:
    """Fill the test-case template with the ticket requirements and requested count."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    prompt = template.replace("[NUMBER]", str(count))
    return prompt.replace("[PASTE REQUIREMENTS HERE]", requirements_text.strip())


def _call_ollama(prompt: str, cfg: dict) -> str:
    """Try the preferred model, then each fallback, until one responds."""
    errors = []
    for model in (OLLAMA_MODEL,) + OLLAMA_FALLBACK_MODELS:
        try:
            payload = {"model": model, "prompt": prompt, "stream": False, "options": OLLAMA_OPTIONS}
            resp = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if data.get("error"):
                raise LLMError(str(data["error"]))
            text = (data.get("response") or "").strip()
            if text:
                return text
            raise LLMError("empty response")
        except Exception as exc:  # noqa: BLE001 - any failure moves to the next model
            errors.append(f"{model}: {exc}")
    raise LLMError("; ".join(errors))


def _call_groq(prompt: str, cfg: dict) -> str:
    key = (cfg.get("groq_key") or "").strip()
    if not key:
        raise LLMError("Groq API key is not configured on the Settings screen.")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a Senior QA Engineer writing test cases."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=GROQ_TIMEOUT)
    resp.raise_for_status()
    text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    if not text:
        raise LLMError("Groq returned an empty response.")
    return text


def generate_test_cases(requirements_text: str, count: int, cfg: dict) -> str:
    """Generate a markdown test-case table for the given requirements.

    Returns the raw LLM markdown.  Raises LLMError only when no provider worked.
    """
    prompt = build_prompt(requirements_text, count)

    if cfg.get("provider") == "ollama":
        # Explicit opt-in to Ollama: try it, fall back to Groq if it fails.
        try:
            return _call_ollama(prompt, cfg)
        except Exception as exc:  # noqa: BLE001 - any failure falls back to Groq
            try:
                return _call_groq(prompt, cfg)
            except Exception as groq_exc:  # noqa: BLE001
                raise LLMError(f"Ollama failed: {exc} | Groq fallback failed: {groq_exc}") from groq_exc

    # Default path: Groq (primary). No silent Ollama attempts.
    return _call_groq(prompt, cfg)
