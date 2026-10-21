"""Configuration: environment variables, ranking weights, suite rules, limits."""

from __future__ import annotations

import os
from importlib import resources


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _default_data_path() -> str:
    """Return the bundled CSV path, falling back to a local path if unpacked."""
    try:
        return str(resources.files("tc_mcp") / "data" / "vwo_5000_test_cases.csv")
    except Exception:  # pragma: no cover - defensive fallback
        return "data/vwo_5000_test_cases.csv"


# Paths and write gating.
DATA_PATH = os.environ.get("TC_MCP_DATA_PATH") or _default_data_path()
OVERLAY_PATH = os.environ.get("TC_MCP_OVERLAY_PATH") or "data/tc_additions.csv"
ALLOW_WRITE = _env_bool("TC_MCP_ALLOW_WRITE", False)
EXPORT_DIR = os.environ.get("TC_MCP_EXPORT_DIR") or "exports"

# Transport.
TRANSPORT = os.environ.get("TC_MCP_TRANSPORT") or "stdio"
PORT = int(os.environ.get("TC_MCP_PORT") or "8000")
AUTH_TOKEN = os.environ.get("TC_MCP_AUTH_TOKEN")

# Response-size limits.
MAX_COMPACT = 100
MAX_FULL = 25
DEFAULT_LIMIT = 20
MAX_GET_KEYS = 25
MAX_ADD = 25
MAX_EXPORT_INLINE = 50

# Priority ordering (low -> high). Used by min_priority / max_priority filters.
PRIORITY_ORDER = ["Low", "Medium", "High", "Highest"]

# Ranking weights.
PRIORITY_WEIGHTS = {"Highest": 40, "High": 30, "Medium": 20, "Low": 10}
STATUS_WEIGHTS = {"Ready": 10, "Automated": 8, "Draft": 2, "Deprecated": 0}
TYPE_WEIGHTS = {
    "Security": 6,
    "Functional": 6,
    "Negative": 5,
    "API": 5,
    "Regression": 4,
    "Boundary": 4,
    "Performance": 3,
    "UI/UX": 2,
    "Accessibility": 2,
}

# Suite rules, tunable here.
SUITE_RULES = {
    "smoke": {
        "priorities": ["Highest"],
        "types": ["Functional", "API", "Security"],
        "per_feature": 1,
        "browser": "Chrome 148",
    },
    "sanity": {
        "priorities": ["Highest", "High"],
        "types": ["Functional", "Negative", "API"],
        "per_feature": 2,
        "browser": None,
    },
    "regression": {
        "priorities": None,  # all priorities
        "types": None,  # all types
        "per_feature": None,  # no cap
        "browser": None,
    },
}

# Generic expected results the linter flags.
GENERIC_EXPECTED_RESULTS = {
    "the feature works as expected",
    "the feature works correctly",
    "test passed",
    "works as expected",
    "no errors found",
    "behavior is correct",
    "the functionality works",
    "result is as expected",
    "as expected",
}
