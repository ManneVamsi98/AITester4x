"""Hybrid retrieval: dense + sparse (RRF) from Qdrant, then cross-encoder rerank."""

from __future__ import annotations

from dataclasses import dataclass

from . import qdrant_store
from .embeddings import get_embedder


@dataclass
class Retrieved:
    text: str
    metadata: dict
    score: float


class Retriever:
    """Lazily wires the embedder, Qdrant client, and reranker (models are heavy)."""

    def __init__(self, settings) -> None:
        self.settings = settings
        self._client = None
        self._embedder = None
        self._reranker = None

    @property
    def client(self):
        if self._client is None:
            self._client = qdrant_store.client_from(self.settings)
        return self._client

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = get_embedder(self.settings)
        return self._embedder

    def ensure_ready(self) -> None:
        qdrant_store.ensure_collection(self.client, self.settings.collection, self.embedder.dim)

    def _rerank(self, query: str, results: list[Retrieved], limit: int) -> list[Retrieved]:
        settings = self.settings
        if not settings.rerank_enabled or not results:
            return results[:limit]
        try:
            if self._reranker is None:
                from FlagEmbedding import FlagReranker

                self._reranker = FlagReranker(settings.reranker_model, use_fp16=False)
            pairs = [[query, r.text] for r in results]
            scores = self._reranker.compute_score(pairs, normalize=True)
            if isinstance(scores, float):
                scores = [scores]
            for result, score in zip(results, scores):
                result.score = float(score)
            results.sort(key=lambda r: r.score, reverse=True)
        except Exception as exc:  # reranker optional — degrade to RRF order
            print(f"  ! reranker unavailable ({exc}); using hybrid RRF order")
        return results[:limit]

    def retrieve(
        self,
        query: str,
        source_types: list[str] | None = None,
        repos: list[str] | None = None,
        top_k: int | None = None,
        limit: int | None = None,
    ) -> list[Retrieved]:
        args = dict(
            top_k=top_k or self.settings.top_k,
            source_types=source_types,
            repos=repos,
        )
        try:
            points = qdrant_store.hybrid_query(
                self.client, self.settings.collection, self.embedder, query, **args
            )
        except Exception:
            # A filtered field needs a payload index; fall back to an unfiltered
            # search rather than failing the whole request.
            if not (source_types or repos):
                raise
            points = qdrant_store.hybrid_query(
                self.client,
                self.settings.collection,
                self.embedder,
                query,
                top_k=top_k or self.settings.top_k,
            )
        results = [
            Retrieved(
                text=(point.payload or {}).get("text", ""),
                metadata={k: v for k, v in (point.payload or {}).items() if k != "text"},
                score=float(point.score or 0.0),
            )
            for point in points
        ]
        return self._rerank(query, results, limit or self.settings.rerank_top_n)
