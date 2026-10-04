"""Lexical sparse encoder (hashed BM25-style term frequencies).

Dependency-free fallback for sparse retrieval. It exists so hybrid search works
even when the dense embedder does not emit native sparse weights (e.g. Ollama),
and so the pipeline can be unit-tested with no ML dependencies at all.

Indices are stable 32-bit hashes of tokens, which is what Qdrant's sparse vector
expects. Exact identifiers (``WING-LOGIN-TC-089``, ``KAN-5``) are kept as whole
tokens and up-weighted, so id/phrase lookups match reliably.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

_WORD = re.compile(r"[A-Za-z0-9_]+")
_ID = re.compile(r"[A-Za-z]+-[A-Za-z0-9]*(?:-[A-Za-z0-9]+)*\d[A-Za-z0-9-]*")

_HASH_SPACE = 2**32


@dataclass
class Sparse:
    indices: list[int]
    values: list[float]


def hash_token(token: str) -> int:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") % _HASH_SPACE


def _normalize(weights: dict[int, float]) -> Sparse:
    if not weights:
        return Sparse([], [])
    indices = sorted(weights)
    values = [weights[i] for i in indices]
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return Sparse(indices, [v / norm for v in values])


class LexicalSparseEncoder:
    """Hashed term-frequency sparse encoder."""

    def encode(self, text: str) -> Sparse:
        counts: dict[str, float] = {}
        for word in _WORD.findall(text.lower()):
            counts[word] = counts.get(word, 0.0) + 1.0
        for ident in _ID.findall(text):
            counts[ident] = counts.get(ident, 0.0) + 3.0
            counts[ident.lower()] = counts.get(ident.lower(), 0.0) + 3.0

        weights: dict[int, float] = {}
        for token, count in counts.items():
            weights[hash_token(token)] = weights.get(hash_token(token), 0.0) + (
                1.0 + math.log(count)
            )
        return _normalize(weights)


def sparse_from_weights(weights: dict[str, float]) -> Sparse:
    """Convert a ``{token: weight}`` mapping (e.g. BGE-M3 lexical weights)."""
    agg: dict[int, float] = {}
    for token, weight in weights.items():
        bucket = hash_token(token)
        agg[bucket] = agg.get(bucket, 0.0) + float(weight)
    return _normalize(agg)
