"""Selenium / Playwright framework repos -> code-aware chunks.

If a source folder is empty, the repo is shallow-cloned from the URL below
(unless offline); otherwise the files already present are ingested.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..chunking import chunk_code
from .base import document, iter_files, read_text

SUFFIXES = [
    ".java", ".js", ".ts", ".tsx", ".jsx", ".py",
    ".json", ".xml", ".properties", ".yml", ".yaml", ".md",
]

REPOS = {
    "01_selenium_framework": "https://github.com/PramodDutta/ATB13xSeleniumAdvanceFramework",
    "02_playwright_framework": "https://github.com/PramodDutta/Advance-Playwright-Framework",
}


def _ensure_repo(repo_dir: Path, url: str) -> str:
    """Clone the repo into ``repo_dir`` if empty. Returns the HEAD commit sha (or '')."""
    if url and not any(repo_dir.iterdir()):
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(repo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"  ! could not clone {url}: {exc}")
            return ""
    try:
        return subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except Exception:
        return ""


def load(settings, folder: str) -> list[dict]:
    base = settings.source_dir(folder)
    base.mkdir(parents=True, exist_ok=True)

    # Clone into base/repo so it sits beside our own placeholder README (git clone
    # needs an empty target). If no repo is present, ingest whatever files you
    # dropped directly into the folder.
    repo_dir = base / "repo"
    repo_dir.mkdir(exist_ok=True)
    commit_sha = _ensure_repo(repo_dir, REPOS.get(folder, ""))
    scan_root = repo_dir if any(repo_dir.iterdir()) else base

    repo = folder.split("_", 1)[1] if "_" in folder else folder
    docs: list[dict] = []
    for path in iter_files(scan_root, SUFFIXES, skip_top_level_readme=(scan_root == base)):
        text = read_text(path)
        if not text.strip():
            continue
        rel = path.relative_to(scan_root).as_posix()
        for index, chunk in enumerate(chunk_code(text)):
            header = f"// File: {rel}\n"
            docs.append(
                document(
                    header + chunk,
                    point_key=f"{folder}:{rel}:{index}",
                    source_type="code",
                    source_file=rel,
                    repo=repo,
                    path=rel,
                    commit_sha=commit_sha or None,
                )
            )
    return docs
