"""Lucid chart text exports -> ~512-token chunks."""

from __future__ import annotations

import json

from ..chunking import chunk_text
from .base import document, iter_files, read_text

SUFFIXES = [".txt", ".md", ".json", ".csv"]


def _json_strings(node) -> list[str]:
    out: list[str] = []
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            out.extend(_json_strings(value))
    elif isinstance(node, list):
        for value in node:
            out.extend(_json_strings(value))
    return out


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    docs: list[dict] = []
    for path in iter_files(base, SUFFIXES):
        if path.suffix.lower() == ".json":
            try:
                text = "\n".join(_json_strings(json.loads(read_text(path))))
            except json.JSONDecodeError:
                text = read_text(path)
        else:
            text = read_text(path)
        if not text.strip():
            continue
        for index, chunk in enumerate(chunk_text(text)):
            docs.append(
                document(
                    chunk,
                    point_key=f"{folder}:{path.name}:{index}",
                    source_type="diagram",
                    source_file=path.name,
                    diagram=path.stem,
                )
            )
    return docs
