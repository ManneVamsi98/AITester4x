"""Configuration: environment variables, category maps, and limits."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent

# The upstream repository that the /skills folder is synced from.
UPSTREAM_REPO = os.environ.get(
    "TSF_MCP_UPSTREAM_REPO", "https://github.com/PramodDutta/skillmasterclass.git"
)
UPSTREAM_SKILLS_SUBDIR = "skillmasterclass/skills"
UPSTREAM_META_FILE = ".upstream.json"

# Transport.
TRANSPORT = os.environ.get("TSF_MCP_TRANSPORT") or "stdio"
PORT = int(os.environ.get("TSF_MCP_PORT") or "8000")
AUTH_TOKEN = os.environ.get("TSF_MCP_AUTH_TOKEN")


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Syncing is a write operation that mutates the local skills folder.
ALLOW_SYNC = _env_bool("TSF_MCP_ALLOW_SYNC", True)

# Response-size limits.
MAX_RESULTS = 50
DEFAULT_LIMIT = 10


def _resolve_skills_dir() -> Path:
    """Return the /skills folder (source of truth), honoring an override.

    Resolution order: TSF_MCP_SKILLS_PATH -> ./skills (cwd) -> repo skills
    (next to the package) -> skills bundled inside the installed package.
    """
    candidates: list[Path] = []
    env = os.environ.get("TSF_MCP_SKILLS_PATH")
    if env:
        candidates.append(Path(env))
    candidates.append(Path.cwd() / "skills")
    candidates.append(PACKAGE_DIR.parent.parent / "skills")
    candidates.append(PACKAGE_DIR / "data" / "skills")

    for candidate in candidates:
        if candidate.is_dir() and any(candidate.rglob("SKILL.md")):
            return candidate
    return candidates[0]


SKILLS_DIR = _resolve_skills_dir()

# Category labels derived from the folder a skill lives in.
STLC_CATEGORY_MAP = {
    "01-requirement-analysis": "STLC · Requirement Analysis",
    "02-test-planning": "STLC · Test Planning",
    "03-test-design": "STLC · Test Design",
    "04-test-case-development": "STLC · Test Case Development",
    "05-test-execution": "STLC · Test Execution",
    "06-defect-management": "STLC · Defect Management",
    "07-test-closure": "STLC · Test Closure",
}

PACK_CATEGORY_MAP = {
    "playwright-pack": "Playwright",
    "selenium-pack": "Selenium",
    "cypress-pack": "Cypress",
    "api-pack": "API Testing",
    "performance-pack": "Performance",
    "security-pack": "Security",
    "automation-pack": "Automation",
}

TOP_CATEGORY_MAP = {
    "llm-eval-pack": "LLM Evaluation",
    "ai-agent-pack": "AI Agents",
    "mcp-pack": "MCP",
}
