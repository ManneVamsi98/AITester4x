"""Persisted settings for the Test Plan Agent.

Reads/writes a single local config.json next to this module (gitignored).
All credentials (Jira token, Groq key) live ONLY there or in .env - never
in source code. .env values seed empty config fields so the app works
before the Settings page is opened.
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"
# .env may sit next to this module or in the chapter root (one level up).
_ENV_CANDIDATES = (Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env")

DEFAULTS = {
    "jira_url": "",
    "jira_email": "",
    "jira_token": "",
    "groq_key": "",
}

_REQUIRED_FOR_JIRA = ("jira_url", "jira_email", "jira_token")

# Maps .env keys (case-insensitive) to config keys.
_ENV_MAP = {
    "JIRA_BASE_URL": "jira_url",
    "JIRA_URL": "jira_url",
    "JIRA_EMAIL": "jira_email",
    "JIRA_API_TOKEN": "jira_token",
    "JIRA_TOKEN": "jira_token",
    "GROQ_KEY": "groq_key",
    "GROQ_API_KEY": "groq_key",
}


def _seed_from_env() -> dict:
    """Read credentials from the first existing .env (chapter root or local).

    Fills only fields the user hasn't already set in config.json.
    """
    seed = {}
    env_path = next((p for p in _ENV_CANDIDATES if p.exists()), None)
    if env_path is None:
        return seed
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            cfg_key = _ENV_MAP.get(key.strip().upper())
            if cfg_key:
                seed[cfg_key] = value.strip()
    except OSError:
        pass
    return seed


def load_config() -> dict:
    """Return settings merged over defaults, seeded from .env. Never raises."""
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if isinstance(stored, dict):
                cfg.update({k: stored[k] for k in DEFAULTS if k in stored})
        except (json.JSONDecodeError, OSError):
            pass
    for key in _ENV_MAP.values():
        if not cfg.get(key):
            cfg[key] = _seed_from_env().get(key, "")
    return cfg


def save_config(cfg: dict) -> None:
    """Persist settings to config.json. Raises OSError on failure."""
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in cfg.items() if k in DEFAULTS})
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2)


def is_configured(cfg: dict) -> bool:
    """True when the Jira credentials needed to fetch tickets are present."""
    return all(bool(cfg.get(k)) for k in _REQUIRED_FOR_JIRA)


def is_provider_ready(cfg: dict) -> bool:
    """True when the LLM provider (Groq) has its key."""
    return bool(cfg.get("groq_key"))
