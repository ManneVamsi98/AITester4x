"""Sync: download the upstream skills into the local /skills folder.

The /skills folder is the source of truth and is committed to the repo. This
module re-pulls the upstream ``skillmasterclass/skills`` tree (via a shallow
git clone) and merges it into the local folder, then rewrites ``.upstream.json``
so every synced skill is labelled ``upstream``.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from tsf_mcp import config


def _run_git(args: list[str], cwd: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _merge_upstream(source: Path, target: Path) -> list[str]:
    """Copy every upstream skill folder into ``target`` and return their names.

    Only upstream skill folders are written; any local (non-upstream) skills
    already in ``target`` are left untouched.
    """
    target.mkdir(parents=True, exist_ok=True)
    upstream_names: list[str] = []
    for skill_md in sorted(source.rglob("SKILL.md")):
        name = skill_md.parent.name
        upstream_names.append(name)

        dest = target / skill_md.parent.relative_to(source)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill_md.parent, dest)

    return upstream_names


def _write_upstream_meta(target: Path, upstream_names: list[str]) -> None:
    meta = {
        "repo": config.UPSTREAM_REPO,
        "source_path": config.UPSTREAM_SKILLS_SUBDIR,
        "upstream_skills": sorted(upstream_names),
    }
    meta_path = target / config.UPSTREAM_META_FILE
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def sync_upstream(target_dir: Path | None = None, repo_url: str | None = None) -> dict:
    """Clone the upstream repo and copy its skills into the target folder.

    Returns a summary dict with counts. Raises subprocess.CalledProcessError if
    the clone fails (e.g. no network or git unavailable).
    """
    target = Path(target_dir) if target_dir else config.SKILLS_DIR

    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = Path(tmp) / "skillmasterclass"
        _run_git(
            ["clone", "--depth", "1", repo_url or config.UPSTREAM_REPO, str(clone_dir)],
            cwd=tmp,
        )

        source = clone_dir / config.UPSTREAM_SKILLS_SUBDIR
        if not source.is_dir():
            raise FileNotFoundError(
                f"Expected '{config.UPSTREAM_SKILLS_SUBDIR}' in {config.UPSTREAM_REPO}, not found."
            )

        upstream_names = _merge_upstream(source, target)

    _write_upstream_meta(target, upstream_names)

    return {
        "synced": len(upstream_names),
        "upstream_skills": upstream_names,
        "repo": repo_url or config.UPSTREAM_REPO,
    }
