"""Pluggable dense + sparse embedders.

Providers
---------
``bge_m3``  BAAI/bge-m3 via FlagEmbedding — production default. One model emits
            both a 1024-d dense vector and native sparse lexical weights.
``ollama``  Local Ollama embeddings (dense only); sparse falls back to the
            dependency-free lexical encoder. Useful on machines without torch.
``hash``    Deterministic, zero-dependency. Smoke tests only — NOT for answers.

Every provider implements ``embed_documents(texts)`` and ``embed_query(text)``,
returning ``(dense: list[float], sparse: Sparse)`` tuples.
"""

from __future__ import annotations

import math
from typing import Protocol

from .sparse import LexicalSparseEncoder, Sparse, hash_token, sparse_from_weights


class Embedder(Protocol):
    dim: int

    def embed_documents(self, texts: list[str]) -> list[tuple[list[float], Sparse]]: ...

    def embed_query(self, text: str) -> tuple[list[float], Sparse]: ...


class HashEmbedder:
    """Deterministic hashed bag-of-words. No dependencies, no semantics."""

    def __init__(self, dim: int = 256) -> None:
        import re

        self.dim = dim
        self._word = re.compile(r"[A-Za-z0-9_]+")
        self._sparse = LexicalSparseEncoder()

    def _dense(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for word in self._word.findall(text.lower()):
            vec[hash_token(word) % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[tuple[list[float], Sparse]]:
        return [(self._dense(t), self._sparse.encode(t)) for t in texts]

    def embed_query(self, text: str) -> tuple[list[float], Sparse]:
        return self._dense(text), self._sparse.encode(text)


class OllamaEmbedder:
    """Dense embeddings from a local Ollama server; lexical sparse fallback."""

    def __init__(self, model: str, url: str) -> None:
        self.model = model
        self.url = url.rstrip("/")
        self._sparse = LexicalSparseEncoder()
        self._dim: int | None = None

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self._dense("dimension probe"))
        return self._dim

    def _dense(self, text: str) -> list[float]:
        import requests

        resp = requests.post(
            f"{self.url}/api/embed",
            json={"model": self.model, "input": text},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"][0]

    def _dense_batch(self, texts: list[str]) -> list[list[float]]:
        import requests

        resp = requests.post(
            f"{self.url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=600,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]

    def embed_documents(self, texts: list[str]) -> list[tuple[list[float], Sparse]]:
        vectors = self._dense_batch(texts)
        if self._dim is None and vectors:
            self._dim = len(vectors[0])
        return [(v, self._sparse.encode(t)) for v, t in zip(vectors, texts)]

    def embed_query(self, text: str) -> tuple[list[float], Sparse]:
        dense = self._dense(text)
        if self._dim is None:
            self._dim = len(dense)
        return dense, self._sparse.encode(text)


class BGEM3Embedder:
    """BAAI/bge-m3 dense + native sparse lexical weights (production default)."""

    def __init__(self, model_name: str = "BAAI/bge-m3", use_fp16: bool = False) -> None:
        from FlagEmbedding import BGEM3FlagModel

        self.model_name = model_name
        self.dim = 1024
        self._model = BGEM3FlagModel(model_name, use_fp16=use_fp16)

    def _encode(self, texts: list[str], batch_size: int):
        return self._model.encode(
            texts,
            batch_size=batch_size,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )

    def embed_documents(self, texts: list[str]) -> list[tuple[list[float], Sparse]]:
        out = self._encode(texts, batch_size=8)
        dense = out["dense_vecs"].tolist()
        lexical = out["lexical_weights"]
        return [(d, sparse_from_weights(w)) for d, w in zip(dense, lexical)]

    def embed_query(self, text: str) -> tuple[list[float], Sparse]:
        return self.embed_documents([text])[0]


def get_embedder(settings) -> Embedder:
    provider = settings.embed_provider
    if provider in {"bge_m3", "bge-m3", "flagembedding", "flag_embedding"}:
        return BGEM3Embedder(settings.embed_model)
    if provider == "ollama":
        return OllamaEmbedder(settings.embed_model, settings.ollama_url)
    if provider == "hash":
        return HashEmbedder()
    raise ValueError(
        f"Unknown EMBED_PROVIDER={provider!r} (expected bge_m3, ollama, or hash)"
    )
