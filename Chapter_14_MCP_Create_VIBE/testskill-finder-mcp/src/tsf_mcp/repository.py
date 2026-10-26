"""Repository: loads the /skills folder and exposes search and lookup."""

from __future__ import annotations

import difflib
import json
from pathlib import Path

from tsf_mcp import config
from tsf_mcp.models import Skill, load_skill
from tsf_mcp.search import SearchIndex


class Repository:
    def __init__(self, skills_dir: str | Path | None = None):
        self.skills_dir = Path(skills_dir) if skills_dir else config.SKILLS_DIR
        self.upstream_names = self._load_upstream_names()
        self.skills: list[Skill] = self._load_skills()
        self.by_name: dict[str, Skill] = {s.name: s for s in self.skills}
        self.index = SearchIndex()
        for skill in self.skills:
            self.index.add(skill)

    def _load_upstream_names(self) -> set[str]:
        meta_file = self.skills_dir / config.UPSTREAM_META_FILE
        if not meta_file.exists():
            return set()
        try:
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            return {str(n) for n in data.get("upstream_skills", [])}
        except (json.JSONDecodeError, OSError):
            return set()

    def _load_skills(self) -> list[Skill]:
        skills: list[Skill] = []
        for skill_md in sorted(self.skills_dir.rglob("SKILL.md")):
            name_hint = skill_md.parent.name
            provenance = "upstream" if name_hint in self.upstream_names else "local"
            skills.append(load_skill(skill_md, self.skills_dir, provenance))
        return skills

    def reload(self) -> None:
        """Re-scan the skills folder (used after sync_skills writes new files)."""
        self.upstream_names = self._load_upstream_names()
        self.skills = self._load_skills()
        self.by_name = {s.name: s for s in self.skills}
        self.index = SearchIndex()
        for skill in self.skills:
            self.index.add(skill)

    def get(self, name: str) -> Skill | None:
        key = name.strip().lower()
        return next(
            (s for s in self.skills if s.name.lower() == key),
            None,
        )

    def all(self) -> list[Skill]:
        return list(self.skills)

    def categories(self) -> list[dict]:
        grouped: dict[str, list[str]] = {}
        for skill in self.skills:
            grouped.setdefault(skill.category, []).append(skill.name)
        return [
            {
                "category": category,
                "count": len(names),
                "skills": sorted(names),
            }
            for category, names in sorted(grouped.items())
        ]

    def stats(self) -> dict:
        upstream = sum(1 for s in self.skills if s.provenance == "upstream")
        return {
            "total_skills": len(self.skills),
            "categories": len(self.categories()),
            "upstream": upstream,
            "local": len(self.skills) - upstream,
        }

    def search(
        self,
        query: str,
        category: str | None = None,
        area: str | None = None,
        provenance: str | None = None,
        limit: int = config.DEFAULT_LIMIT,
    ) -> list[dict]:
        hits = self.index.search(query, category, area, provenance)
        rows = []
        for hit in hits[:limit]:
            row = hit.skill.to_summary()
            row["score"] = round(hit.score, 1)
            row["matched_fields"] = hit.matched
            rows.append(row)
        return rows

    def suggest(self, query: str, limit: int = 5) -> dict:
        """'Did you mean' plus related skills for a query that may be misspelled."""
        from tsf_mcp.search import tokenize

        vocab: set[str] = set()
        for s in self.skills:
            vocab.update(tokenize(s.name))
            vocab.update(tokenize(s.description))
            vocab.update(tokenize(s.category))

        raw = tokenize(query)
        corrected: list[str] = []
        for tok in raw:
            matches = difflib.get_close_matches(tok, sorted(vocab), n=1, cutoff=0.75)
            corrected.append(matches[0] if matches else tok)

        corrected_query = " ".join(corrected)
        did_you_mean = [c for c, r in zip(corrected, raw) if c != r]
        related = self.search(corrected_query, limit=limit)
        return {
            "query": query,
            "did_you_mean": did_you_mean,
            "corrected_query": corrected_query,
            "related": related,
        }
