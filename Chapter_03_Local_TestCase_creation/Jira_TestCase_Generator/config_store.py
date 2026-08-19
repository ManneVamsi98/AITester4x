"""Persisted settings layer for the Jira Test Case Generator.

Reads/writes a single local JSON file (config.json) sitting next to this module.
The file is excluded from version control via the folder's .gitignore.
All credentials (Jira token, Groq key) live ONLY in this file - never in source code.
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"
ENV_PATH = Path(__file__).parent / ".env"

DEFAULTS = {
    "jira_url": "",
    "jira_email": "",
    "jira_token": "",
    "provider": "groq",  # "groq" (default - Ollama is unreliable locally) or "ollama"
    "groq_key": "",
    "default_tc_count": 10,
}

# Fields that must be non-empty for the chat screen to work end to end.
_REQUIRED_FOR_JIRA = ("jira_url", "jira_email", "jira_token")

# Maps .env keys (case-insensitive) to config keys.
_ENV_MAP = {
    "JIRA_URL": "jira_url",
    "JIRA_EMAIL": "jira_email",
    "JIRA_API_TOKEN": "jira_token",
    "JIRA_TOKEN": "jira_token",
    "GROQ_KEY": "groq_key",
    "GROQ_API_KEY": "groq_key",
}


def _seed_from_env() -> dict:
    """Read credentials from the local .env file (manual reference), if present.

    Only fills fields the user hasn't already set in config.json. Returns {} when
    the .env is missing. .env is gitignored - never ship credentials in code.
    """
    seed = {}
    if not ENV_PATH.exists():
        return seed
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
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
    """Return the current settings as a dict, merged over defaults.

    Missing/corrupt config.json falls back to defaults, then to values seeded
    from the local .env (so the app works without first opening Settings).
    Never raises.
    """
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if isinstance(stored, dict):
                cfg.update({k: stored[k] for k in DEFAULTS if k in stored})
                # Guard against a manually corrupted type for the count field.
                try:
                    cfg["default_tc_count"] = int(cfg["default_tc_count"])
                except (TypeError, ValueError):
                    cfg["default_tc_count"] = DEFAULTS["default_tc_count"]
        except (json.JSONDecodeError, OSError):
            pass
    # Seed any still-empty fields from .env.
    for key in _ENV_MAP.values():
        if not cfg.get(key):
            cfg[key] = _seed_from_env().get(key, "")
    return cfg


def save_config(cfg: dict) -> None:
    """Persist settings to config.json.

    Raises OSError on failure so the caller (Settings screen) can surface it.
    """
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in cfg.items() if k in DEFAULTS})
    try:
        merged["default_tc_count"] = int(merged["default_tc_count"])
    except (TypeError, ValueError):
        merged["default_tc_count"] = DEFAULTS["default_tc_count"]

    # Sanitize provider to one of the two supported values.
    merged["provider"] = "groq" if merged["provider"] == "groq" else "ollama"

    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2)


def is_configured(cfg: dict) -> bool:
    """True when the Jira credentials needed to fetch tickets are present."""
    return all(bool(cfg.get(k)) for k in _REQUIRED_FOR_JIRA)


def is_provider_ready(cfg: dict) -> bool:
    """True when the selected provider has what it needs to run.

    Ollama needs nothing stored (local server assumed running); Groq needs a key.
    """
    if cfg.get("provider") == "groq":
        return bool(cfg.get("groq_key"))
    return True
