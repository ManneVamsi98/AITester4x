"""Retrieval quality harness: recall@1/5/10 and MRR.

Usage:
    python scripts/eval_retrieval.py [labels.json]

Label file format (list):
    [{"query": "...", "expect_tc_id": "WING-LOGIN-TC-002"},
     {"query": "...", "expect_contains": "authentication-server-error"}]

With no argument a small built-in set (the Chapter 11 sanity checks) is used.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qabuddy.config import Settings  # noqa: E402
from qabuddy.retrieval import Retriever  # noqa: E402

DEFAULT_LABELS = [
    {"query": "test case that verifies the login page load", "expect_tc_id": "LOGIN-001"},
    {"query": "login failure on the VWO app with valid credentials", "expect_contains": "VWO-26"},
    {"query": "CI login tests fail because the IP address or location did not match", "expect_contains": "QAB-101"},
]


def _matches(item, label: dict) -> bool:
    if "expect_tc_id" in label:
        return item.metadata.get("tc_id") == label["expect_tc_id"]
    if "expect_contains" in label:
        needle = label["expect_contains"].lower()
        return needle in item.text.lower() or needle in str(item.metadata).lower()
    return False


def main() -> None:
    labels_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    labels = json.loads(labels_path.read_text()) if labels_path else DEFAULT_LABELS

    settings = Settings.load()
    retriever = Retriever(settings)
    retriever.ensure_ready()

    hits_at = {1: 0, 5: 0, 10: 0}
    reciprocal_ranks = []
    for label in labels:
        results = retriever.retrieve(label["query"], top_k=10, limit=10)
        rank = next((i for i, item in enumerate(results, start=1) if _matches(item, label)), None)
        for k in hits_at:
            if rank and rank <= k:
                hits_at[k] += 1
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
        print(f"[{'hit ' + str(rank) if rank else 'MISS'}] {label['query']}")

    total = len(labels) or 1
    print()
    for k in (1, 5, 10):
        print(f"recall@{k}: {hits_at[k] / total:.3f}")
    print(f"MRR:      {sum(reciprocal_ranks) / total:.3f}")

    report = {
        "labels": len(labels),
        "recall@1": hits_at[1] / total,
        "recall@5": hits_at[5] / total,
        "recall@10": hits_at[10] / total,
        "mrr": sum(reciprocal_ranks) / total,
    }
    out = settings.output_dir / "eval_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
