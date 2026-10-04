"""Source registry — maps a short source key to its data folder and adapter."""

from __future__ import annotations

from . import diagrams, documents, jenkins, jira, repositories, testcases, transcripts

# key -> (data folder, adapter module)
SOURCES: dict[str, tuple[str, object]] = {
    "selenium": ("01_selenium_framework", repositories),
    "playwright": ("02_playwright_framework", repositories),
    "testcases": ("03_test_cases", testcases),
    "jira": ("04_jira", jira),
    "company_docs": ("05_company_docs", documents),
    "meeting_notes": ("07_meeting_notes", transcripts),
    "lucid_charts": ("08_lucid_charts", diagrams),
    "prd": ("09_prd_srs_brd", documents),
    "jenkins": ("10_jenkins_logs", jenkins),
}

# Reserved for Phase 2 (never ingested in Phase 1)
PHASE_2: dict[str, str] = {"figma": "06_figma_designs"}

ALL_KEYS = list(SOURCES)


def load_source(settings, key: str) -> list[dict]:
    if key not in SOURCES:
        raise KeyError(
            f"Unknown source {key!r}. Valid: {', '.join(SOURCES)}"
            + (f" (Phase 2: {', '.join(PHASE_2)})" if PHASE_2 else "")
        )
    folder, adapter = SOURCES[key]
    return adapter.load(settings, folder)
