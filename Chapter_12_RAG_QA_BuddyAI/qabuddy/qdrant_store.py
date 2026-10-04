"""Qdrant collection management + hybrid (dense + sparse, RRF) search.

A single collection stores two named vectors per point: ``dense`` (the semantic
vector) and ``sparse`` (lexical weights). Queries run both and fuse the ranked
lists with Reciprocal Rank Fusion inside Qdrant.
"""

from __future__ import annotations

import uuid
from typing import Any, Iterable

from .sparse import Sparse

DENSE = "dense"
SPARSE = "sparse"

_POINT_NAMESPACE = uuid.UUID("6f1d7c2e-6a63-4a0e-9c1b-2f9a2a4c1f77")


def make_point_id(point_key: str) -> str:
    """Deterministic id so re-ingestion updates a point instead of duplicating."""
    return str(uuid.uuid5(_POINT_NAMESPACE, point_key))


def client_from(settings, cloud: bool = False):
    from qdrant_client import QdrantClient

    if cloud:
        return QdrantClient(
            url=settings.qdrant_cloud_url,
            api_key=settings.qdrant_api_key,
            cloud_inference=True,
        )
    return QdrantClient(url=settings.qdrant_url)


def ensure_payload_indexes(client, name: str) -> None:
    """Keyword indexes for the fields we filter on.

    Qdrant requires an index before a field can be used in a filter, so create
    these up front; ignore "already exists" on re-runs.
    """
    from qdrant_client import models as qm

    for field in ("source_type", "repo"):
        try:
            client.create_payload_index(
                collection_name=name,
                field_name=field,
                field_schema=qm.PayloadSchemaType.KEYWORD,
                wait=True,
            )
        except Exception:
            pass


def ensure_collection(client, name: str, dim: int) -> None:
    from qdrant_client import models as qm

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config={DENSE: qm.VectorParams(size=dim, distance=qm.Distance.COSINE)},
            sparse_vectors_config={SPARSE: qm.SparseVectorParams()},
        )
        ensure_payload_indexes(client, name)
        return

    info = client.get_collection(name)
    params = info.config.params.vectors
    existing = params[DENSE].size if isinstance(params, dict) else params.size
    if existing != dim:
        raise RuntimeError(
            f"Collection '{name}' has dense dim {existing} but the embedder emits {dim}. "
            "Re-embed with the matching model, or delete the collection and re-ingest "
            "(e.g. set QDRANT_COLLECTION to a new name)."
        )
    ensure_payload_indexes(client, name)


def _to_sparse_vector(sparse: Sparse):
    from qdrant_client import models as qm

    return qm.SparseVector(indices=sparse.indices, values=sparse.values)


def _clean(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in payload.items():
        if value is None:
            continue
        out[key] = str(value) if not isinstance(value, (str, int, float, bool, list)) else value
    return out


def upsert_chunks(client, collection: str, chunks: list[dict], embedder, batch_size: int = 32) -> int:
    """Embed and upsert ``[{"text", "metadata", "point_key"}]`` chunks. Returns count."""
    from qdrant_client import models as qm

    total = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        texts = [c["text"] for c in batch]
        embedded = embedder.embed_documents(texts)
        points = []
        for chunk, (dense, sparse) in zip(batch, embedded):
            payload = _clean(chunk.get("metadata", {}))
            payload["text"] = chunk["text"]
            points.append(
                qm.PointStruct(
                    id=make_point_id(chunk["point_key"]),
                    vector={DENSE: dense, SPARSE: _to_sparse_vector(sparse)},
                    payload=payload,
                )
            )
        client.upsert(collection_name=collection, points=points, wait=True)
        total += len(points)
    return total


def ensure_cloud_collection(client, name: str, dim: int) -> None:
    """Create a Cloud-Inference collection with a single unnamed vector.

    Cloud Inference writes a ``Document(text, model)`` as the point's vector, so
    the collection must use one unnamed vector (not the named dense+sparse pair
    used by the local, self-embedded collection).
    """
    from qdrant_client import models as qm

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
        )
    ensure_payload_indexes(client, name)


def cloud_upsert_chunks(client, collection: str, chunks: list[dict], model: str, batch_size: int = 64) -> int:
    """Upsert into Qdrant Cloud letting its Inference API embed the text.

    The point vector is a ``Document(text, model)`` rather than a precomputed
    vector, so the free hosted embedding models do the work server-side.
    """
    from qdrant_client import models as qm

    total = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        points = []
        for chunk in batch:
            payload = _clean(chunk.get("metadata", {}))
            payload["text"] = chunk["text"]
            points.append(
                qm.PointStruct(
                    id=make_point_id(chunk["point_key"]),
                    vector=qm.Document(text=chunk["text"], model=model),
                    payload=payload,
                )
            )
        client.upsert(collection_name=collection, points=points, wait=True)
        total += len(points)
    return total


def build_filter(source_types: Iterable[str] | None = None, repos: Iterable[str] | None = None):
    from qdrant_client import models as qm

    conditions = []
    if source_types:
        conditions.append(
            qm.FieldCondition(key="source_type", match=qm.MatchAny(any=list(source_types)))
        )
    if repos:
        conditions.append(qm.FieldCondition(key="repo", match=qm.MatchAny(any=list(repos))))
    if not conditions:
        return None
    return qm.Filter(must=conditions)


def hybrid_query(
    client,
    collection: str,
    embedder,
    query: str,
    top_k: int = 25,
    source_types: Iterable[str] | None = None,
    repos: Iterable[str] | None = None,
):
    from qdrant_client import models as qm

    dense, sparse = embedder.embed_query(query)
    response = client.query_points(
        collection_name=collection,
        prefetch=[
            qm.Prefetch(query=dense, using=DENSE, limit=top_k),
            qm.Prefetch(query=_to_sparse_vector(sparse), using=SPARSE, limit=top_k),
        ],
        query=qm.FusionQuery(fusion=qm.Fusion.RRF),
        query_filter=build_filter(source_types, repos),
        limit=top_k,
        with_payload=True,
    )
    return response.points


def delete_by_source(client, collection: str, source_type: str) -> None:
    from qdrant_client import models as qm

    client.delete(
        collection_name=collection,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(
                must=[qm.FieldCondition(key="source_type", match=qm.MatchValue(value=source_type))]
            )
        ),
        wait=True,
    )


def count(client, collection: str) -> int:
    if not client.collection_exists(collection):
        return 0
    return client.count(collection_name=collection, exact=True).count
