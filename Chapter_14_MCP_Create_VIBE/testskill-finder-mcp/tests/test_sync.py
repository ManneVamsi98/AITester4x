"""Sync tests: the merge + provenance logic (no network / git required)."""

from __future__ import annotations

import json

from tsf_mcp.sync import _merge_upstream, _write_upstream_meta


_SKILL = """---
name: {name}
description: Test skill for {name}.
license: MIT
metadata:
  author: Test
  version: 1.0.0
---

# {name}

## When to use
- ...

## Workflow
1. ...

## Output shape
```
...
```

## Guardrails
- ...
"""


def _make_skill(folder: Path, name: str) -> None:
    (folder / name).mkdir(parents=True)
    (folder / name / "SKILL.md").write_text(_SKILL.format(name=name), encoding="utf-8")


def test_merge_upstream_copies_and_lists(tmp_path):
    source = tmp_path / "source" / "framework-packs" / "playwright-pack"
    _make_skill(source, "pw-alpha")
    _make_skill(source, "pw-beta")

    target = tmp_path / "target"
    # A local (non-upstream) skill should survive the merge untouched.
    local = target / "framework-packs" / "cypress-pack" / "cy-local"
    local.mkdir(parents=True)
    (local / "SKILL.md").write_text("local", encoding="utf-8")

    names = _merge_upstream(source.parent.parent, target)

    assert sorted(names) == ["pw-alpha", "pw-beta"]
    assert (target / "framework-packs" / "playwright-pack" / "pw-alpha" / "SKILL.md").exists()
    assert (target / "framework-packs" / "cypress-pack" / "cy-local" / "SKILL.md").exists()


def test_write_upstream_meta(tmp_path):
    _write_upstream_meta(tmp_path, ["pw-alpha", "pw-beta"])
    data = json.loads((tmp_path / ".upstream.json").read_text(encoding="utf-8"))
    assert data["upstream_skills"] == ["pw-alpha", "pw-beta"]
    assert data["source_path"] == "skillmasterclass/skills"
