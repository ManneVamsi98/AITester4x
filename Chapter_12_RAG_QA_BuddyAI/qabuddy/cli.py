"""Command line entry point.

    python -m qabuddy.cli ingest --source all
    python -m qabuddy.cli ingest --source testcases --recreate
    python -m qabuddy.cli stats
    python -m qabuddy.cli ask "Find the test case for submitting login with Enter"
"""

from __future__ import annotations

import argparse
import sys

from . import qdrant_store
from .config import Settings
from .embeddings import get_embedder
from .ingest import ALL_KEYS, SOURCES, load_source


def cmd_ingest(args) -> None:
    settings = Settings.load()
    keys = ALL_KEYS if args.source == "all" else [args.source]

    embedder = get_embedder(settings)
    client = qdrant_store.client_from(settings)
    if args.recreate and client.collection_exists(settings.collection):
        print(f"Recreating collection '{settings.collection}'")
        client.delete_collection(settings.collection)
    qdrant_store.ensure_collection(client, settings.collection, embedder.dim)

    grand_total = 0
    for key in keys:
        folder = SOURCES[key][0]
        print(f"-> {key} ({folder})")
        try:
            docs = load_source(settings, key)
        except Exception as exc:  # one bad source must not stop the rest
            print(f"   ! {key} failed: {exc}")
            continue
        if not docs:
            print("   . 0 documents")
            continue
        count = qdrant_store.upsert_chunks(client, settings.collection, docs, embedder)
        grand_total += count
        print(f"   OK {count} chunks")

    print(
        f"Upserted {grand_total} chunks. "
        f"Collection '{settings.collection}' now holds {qdrant_store.count(client, settings.collection)} points."
    )


def cmd_stats(args) -> None:
    settings = Settings.load()
    client = qdrant_store.client_from(settings)
    print(f"Qdrant:      {settings.qdrant_url}")
    print(f"Collection:  {settings.collection}")
    print(f"Points:      {qdrant_store.count(client, settings.collection)}")
    print(f"Embedder:    {settings.embed_provider} ({settings.embed_model})")


def cmd_ask(args) -> None:
    from . import rag
    from .retrieval import Retriever

    settings = Settings.load()
    retriever = Retriever(settings)
    contexts = retriever.retrieve(args.question, source_types=args.source or None)
    print(rag.generate(settings, args.question, contexts))
    print()
    for number, item in enumerate(contexts, start=1):
        print(f"[{number}] {item.metadata.get('source_file')} (score {item.score:.4f})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qabuddy", description="QABuddy.ai hybrid RAG")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="load, chunk, embed and index sources")
    ingest.add_argument("--source", default="all", choices=ALL_KEYS + ["all"])
    ingest.add_argument("--recreate", action="store_true", help="drop the collection first")
    ingest.set_defaults(func=cmd_ingest)

    stats = sub.add_parser("stats", help="show collection info")
    stats.set_defaults(func=cmd_stats)

    ask = sub.add_parser("ask", help="ask one question from the terminal")
    ask.add_argument("question")
    ask.add_argument("--source", action="append", help="filter by source_type (repeatable)")
    ask.set_defaults(func=cmd_ask)

    return parser


def main(argv: list[str] | None = None) -> None:
    # Windows consoles default to cp1252; generated answers can contain Unicode
    # (em dashes, non-breaking hyphens). Never crash the CLI on unprintable output.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
