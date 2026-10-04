"""Populate Qdrant Cloud (free cluster + Cloud Inference) from the local sources.

Requires QDRANT_CLOUD_URL and QDRANT_API_KEY in .env. Reuses the same ingestion
adapters as the local pipeline; the hosted collection is dense-only with
``sentence-transformers/all-MiniLM-L6-v2`` (384-d) embedded server-side.

Run:  python scripts/ingest_cloud.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qabuddy import qdrant_store  # noqa: E402
from qabuddy.config import Settings  # noqa: E402
from qabuddy.ingest import ALL_KEYS, load_source  # noqa: E402

CLOUD_DIM = 384  # sentence-transformers/all-MiniLM-L6-v2


def main() -> None:
    settings = Settings.load()
    if not (settings.qdrant_cloud_url and settings.qdrant_api_key):
        print("Set QDRANT_CLOUD_URL and QDRANT_API_KEY in .env first.")
        return

    client = qdrant_store.client_from(settings, cloud=True)
    if client.collection_exists(settings.collection):
        print(f"Recreating collection '{settings.collection}'")
        client.delete_collection(settings.collection)
    qdrant_store.ensure_cloud_collection(client, settings.collection, CLOUD_DIM)

    total = 0
    for key in ALL_KEYS:
        docs = load_source(settings, key)
        if not docs:
            print(f"  {key:16} 0")
            continue
        count = qdrant_store.cloud_upsert_chunks(
            client, settings.collection, docs, settings.cloud_embed_model
        )
        total += count
        print(f"  {key:16} {count}")

    print(
        f"Uploaded {total} chunks to '{settings.collection}' using {settings.cloud_embed_model}; "
        f"cloud count = {qdrant_store.count(client, settings.collection)}"
    )


if __name__ == "__main__":
    main()
