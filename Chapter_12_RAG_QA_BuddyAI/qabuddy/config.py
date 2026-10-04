"""Environment-driven settings.

Kept dependency-light: python-dotenv is optional so the pure-logic modules
(and their tests) import without the heavy runtime stack installed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:  # optional — present in the container, not required for unit tests
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:  # pragma: no cover - import guard
    pass


def _get(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _get_any(names: list[str], default: str = "") -> str:
    """First non-empty value among ``names`` (case-insensitive)."""
    lowered = {key.lower(): value for key, value in os.environ.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value:
            return value
    return default


def _url(value: str) -> str:
    value = (value or "").strip().strip('"').strip("'").rstrip("/")
    if value and not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name) or default)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    root: Path
    data_dir: Path
    output_dir: Path
    groq_key: str
    groq_model: str
    qdrant_url: str
    collection: str
    qdrant_cloud_url: str
    qdrant_api_key: str
    cloud_embed_model: str
    embed_provider: str
    embed_model: str
    ollama_url: str
    rerank_enabled: bool
    reranker_model: str
    top_k: int
    rerank_top_n: int
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_jql: str

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            root=ROOT,
            data_dir=ROOT / "data",
            output_dir=ROOT / "output",
            groq_key=_get("GROQ_KEY"),
            groq_model=_get("GROQ_MODEL", "openai/gpt-oss-120b"),
            qdrant_url=_get("QDRANT_URL", "http://localhost:6333"),
            collection=_get("QDRANT_COLLECTION", "qabuddy"),
            qdrant_cloud_url=_url(
                _get_any(["QDRANT_CLOUD_URL", "QDRANT_CLUSTER_ENDPOINT", "QDRANT_ENDPOINT"])
            ),
            qdrant_api_key=_get_any(["QDRANT_API_KEY"]),
            cloud_embed_model=_get("CLOUD_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            embed_provider=_get("EMBED_PROVIDER", "bge_m3").lower(),
            embed_model=_get("EMBED_MODEL", "BAAI/bge-m3"),
            ollama_url=_get("OLLAMA_URL", "http://localhost:11434"),
            rerank_enabled=_bool("RERANK_ENABLED", True),
            reranker_model=_get("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"),
            top_k=_int("TOP_K", 25),
            rerank_top_n=_int("RERANK_TOP_N", 6),
            jira_base_url=_get("JIRA_BASE_URL"),
            jira_email=_get("JIRA_EMAIL"),
            jira_api_token=_get("JIRA_API_TOKEN"),
            jira_jql=_get("JIRA_JQL"),
        )

    def source_dir(self, folder: str) -> Path:
        return self.data_dir / folder
