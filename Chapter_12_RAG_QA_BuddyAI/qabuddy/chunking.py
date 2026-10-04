"""Source-aware chunkers.

Chunk granularity follows the source's "atomic answer unit": prose and code are
split on structure, logs on build/test boundaries, while test-case rows and JIRA
tickets are indexed whole and never reach these functions.

Token counts are approximated as ``len(text) // 4`` to avoid a tokenizer
dependency; the targets mirror the sizes documented in ``plan.md``.
"""

from __future__ import annotations

import re

CHARS_PER_TOKEN = 4

_PROSE_SEPARATORS = ["\n\n\n", "\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]
_MARKDOWN_SEPARATORS = ["\n## ", "\n### ", "\n# ", "\n\n", "\n", ". ", " "]
_CODE_SEPARATORS = [
    "\nclass ",
    "\npublic ",
    "\nprivate ",
    "\nprotected ",
    "\ndef ",
    "\nfunction ",
    "\nexport ",
    "\ndescribe(",
    "\ntest(",
    "\nit(",
    "\n\n",
    "\n",
    " ",
]

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_LOG_BOUNDARY = re.compile(
    r"(?=^[=\-]{3,}\s*$)|(?=^(?:BUILD|Test Suite|Running|ERROR|FAILED|Finished:)\b)",
    re.MULTILINE,
)


def approx_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_recursive(text: str, max_chars: int, separators: list[str]) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    for index, sep in enumerate(separators):
        if sep in text:
            parts = text.split(sep)
            pieces = [parts[0]] + [sep + p for p in parts[1:]]
            result: list[str] = []
            for piece in pieces:
                if len(piece) <= max_chars:
                    result.append(piece)
                else:
                    result.extend(_split_recursive(piece, max_chars, separators[index + 1 :]))
            return result
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]


def _merge(pieces: list[str], max_chars: int, overlap_chars: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if not piece:
            continue
        if current and len(current) + len(piece) > max_chars:
            chunks.append(current.strip())
            tail = current[-overlap_chars:] if overlap_chars > 0 else ""
            current = f"{tail}\n{piece}" if tail else piece
        else:
            current = f"{current}\n{piece}" if current else piece
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if c.strip()]


def chunk_text(
    text: str,
    max_tokens: int = 512,
    overlap: float = 0.15,
    markdown: bool = False,
    separators: list[str] | None = None,
) -> list[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    max_chars = max_tokens * CHARS_PER_TOKEN
    seps = separators or (_MARKDOWN_SEPARATORS if markdown else _PROSE_SEPARATORS)
    return _merge(_split_recursive(text, max_chars, seps), max_chars, int(max_chars * overlap))


def chunk_code(text: str, max_tokens: int = 500, overlap: float = 0.12) -> list[str]:
    return chunk_text(text, max_tokens, overlap, separators=_CODE_SEPARATORS)


def chunk_transcript(text: str, max_tokens: int = 400, overlap: float = 0.2) -> list[str]:
    return chunk_text(text, max_tokens, overlap, separators=["\n\n", "\n"])


def chunk_log(text: str, max_tokens: int = 700, overlap: float = 0.1) -> list[str]:
    text = normalize_whitespace(strip_ansi(text))
    if not text:
        return []
    max_chars = max_tokens * CHARS_PER_TOKEN
    pieces: list[str] = []
    for part in _LOG_BOUNDARY.split(text):
        if not part or not part.strip():
            continue
        if len(part) <= max_chars:
            pieces.append(part)
        else:
            pieces.extend(_split_recursive(part, max_chars, ["\n", " "]))
    return _merge(pieces, max_chars, int(max_chars * overlap))
