"""Shared ingestion helpers.

A "document" here is the dict shape ``upsert_chunks`` expects:
``{"text": str, "metadata": dict, "point_key": str}``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

# Folder-level READMEs are our own "what goes here" notes, not knowledge to index.
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def document(text: str, point_key: str, source_type: str, source_file, **metadata) -> dict:
    meta = {
        "source_type": source_type,
        "source_file": str(source_file),
        "ingested_at": now_iso(),
    }
    meta.update({k: v for k, v in metadata.items() if v not in (None, "")})
    return {"text": text, "metadata": meta, "point_key": point_key}


def iter_files(
    folder: Path,
    suffixes: Iterable[str],
    skip_top_level_readme: bool = True,
) -> Iterator[Path]:
    if not folder.exists():
        return
    allowed = {s.lower() for s in suffixes}
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in allowed:
            continue
        if skip_top_level_readme and path.name.lower() == "readme.md" and path.parent == folder:
            continue
        yield path


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return ""
