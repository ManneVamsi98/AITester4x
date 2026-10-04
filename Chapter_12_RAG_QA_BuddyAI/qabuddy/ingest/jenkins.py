"""Jenkins / CI logs -> log-aware chunks (~600-800 tokens)."""

from __future__ import annotations

from ..chunking import chunk_log
from .base import document, iter_files, read_text

SUFFIXES = [".log", ".txt", ".xml"]


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    docs: list[dict] = []
    for path in iter_files(base, SUFFIXES):
        text = read_text(path)
        if not text.strip():
            continue
        for index, chunk in enumerate(chunk_log(text)):
            docs.append(
                document(
                    chunk,
                    point_key=f"{folder}:{path.name}:{index}",
                    source_type="jenkins_log",
                    source_file=path.name,
                )
            )
    return docs
