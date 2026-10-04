"""Meeting notes / transcripts -> speaker-turn windows (~300-500 tokens)."""

from __future__ import annotations

from ..chunking import chunk_transcript
from .base import document, iter_files, read_text

SUFFIXES = [".txt", ".md", ".vtt"]


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    docs: list[dict] = []
    for path in iter_files(base, SUFFIXES):
        text = read_text(path)
        if not text.strip():
            continue
        for index, chunk in enumerate(chunk_transcript(text)):
            docs.append(
                document(
                    chunk,
                    point_key=f"{folder}:{path.name}:{index}",
                    source_type="transcript",
                    source_file=path.name,
                )
            )
    return docs
