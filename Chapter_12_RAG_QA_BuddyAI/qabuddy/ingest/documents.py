"""Prose documents (PDF / Markdown / DOCX / TXT) -> ~512-token chunks."""

from __future__ import annotations

from pathlib import Path

from ..chunking import chunk_text
from .base import document, iter_files, read_text

SUFFIXES = [".md", ".txt", ".pdf", ".docx"]


def _pdf_units(path: Path):
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    for number, page in enumerate(reader.pages, start=1):
        yield number, page.extract_text() or ""


def _docx_text(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    docs: list[dict] = []
    for path in iter_files(base, SUFFIXES):
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            units = _pdf_units(path)
        elif suffix == ".docx":
            units = [(None, _docx_text(path))]
        else:
            units = [(None, read_text(path))]

        for page, text in units:
            if not text or not text.strip():
                continue
            for index, chunk in enumerate(chunk_text(text, markdown=(suffix == ".md"))):
                docs.append(
                    document(
                        chunk,
                        point_key=f"{folder}:{path.name}:{page}:{index}",
                        source_type="document",
                        source_file=path.name,
                        page=page,
                    )
                )
    return docs
