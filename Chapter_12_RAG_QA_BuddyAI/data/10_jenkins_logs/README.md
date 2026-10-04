# 10 — Jenkins logs & results

**Put here:** CI logs/results as `.log`, `.txt`, or JUnit `.xml` reports.

**Ingested by:** `qabuddy.ingest.jenkins` — log-aware chunking on build/test boundaries,
~600–800 tokens with 10% overlap; ANSI codes stripped and timestamps normalized.
