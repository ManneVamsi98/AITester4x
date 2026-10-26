"""Skill model and SKILL.md parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tsf_mcp import config


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a SKILL.md into (frontmatter dict, body).

    The frontmatter is the YAML between the opening ``---`` and the next line
    that is exactly ``---``. Bare ``---`` lines in the body (there are none,
    but body markers are ``--- HUMAN REVIEW GATE ---``) are not mistaken for
    the closing delimiter because only a line that is exactly ``---`` counts.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :]).strip()
            try:
                data = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                data = {}
            if not isinstance(data, dict):
                data = {}
            return data, body

    return {}, text


def derive_category(rel_parts: list[str]) -> str:
    """Map a skill's relative path parts to a human-friendly category label."""
    if not rel_parts:
        return "Other"
    first = rel_parts[0]
    if first == "framework-packs" and len(rel_parts) > 1:
        pack = rel_parts[1]
        return config.PACK_CATEGORY_MAP.get(pack, pack.replace("-pack", "").title())
    if first in config.STLC_CATEGORY_MAP:
        return config.STLC_CATEGORY_MAP[first]
    if first in config.TOP_CATEGORY_MAP:
        return config.TOP_CATEGORY_MAP[first]
    return first


@dataclass
class Skill:
    name: str
    description: str
    license: str
    metadata: dict[str, Any]
    body: str
    path: str
    category: str
    area: str
    provenance: str
    content: str = field(repr=False)

    def to_summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "area": self.area,
            "provenance": self.provenance,
            "path": self.path,
        }

    def to_detail(self) -> dict[str, Any]:
        return {
            **self.to_summary(),
            "license": self.license,
            "metadata": self.metadata,
            "content": self.content,
        }


def load_skill(skill_md: Path, skills_dir: Path, provenance: str = "local") -> Skill:
    """Load one SKILL.md file into a Skill, deriving category and area."""
    text = skill_md.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    name = str(fm.get("name") or skill_md.parent.name)
    description = str(fm.get("description") or "").strip()
    license_ = str(fm.get("license") or "MIT")
    metadata = fm.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    rel = skill_md.relative_to(skills_dir)
    parts = list(rel.parts)
    category = derive_category(parts)

    area = (
        metadata.get("stlc-phase")
        or metadata.get("pack")
        or metadata.get("area")
        or category
    )

    return Skill(
        name=name,
        description=description,
        license=license_,
        metadata=metadata,
        body=body,
        path=rel.as_posix(),
        category=category,
        area=str(area),
        provenance=provenance,
        content=text,
    )
