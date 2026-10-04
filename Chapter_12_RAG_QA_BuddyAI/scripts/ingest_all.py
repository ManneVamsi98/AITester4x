"""Ingest every Phase 1 source.

Run from the chapter root:  python scripts/ingest_all.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qabuddy.cli import main  # noqa: E402

if __name__ == "__main__":
    main(["ingest", "--source", "all"])
