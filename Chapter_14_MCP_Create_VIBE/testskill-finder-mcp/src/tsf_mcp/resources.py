"""Resources: read-only context a client can attach (@-mention)."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from tsf_mcp.repository import Repository


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.resource(
        "tsf://catalog",
        name="catalog",
        description="The full skill catalog: name, description, category, area, provenance.",
    )
    def catalog() -> str:
        return json.dumps(
            {"skills": [s.to_summary() for s in repo.all()]},
            indent=2,
        )

    @mcp.resource(
        "tsf://categories",
        name="categories",
        description="Every category with its skill count and names.",
    )
    def categories() -> str:
        return json.dumps(
            {"categories": repo.categories(), "stats": repo.stats()},
            indent=2,
        )

    @mcp.resource(
        "tsf://stats",
        name="stats",
        description="Headline numbers: total, categories, upstream vs local.",
    )
    def stats() -> str:
        return json.dumps(repo.stats(), indent=2)

    @mcp.resource(
        "tsf://skill/{name}",
        name="skill",
        description="One skill's full SKILL.md by name.",
    )
    def skill(name: str) -> str:
        skill = repo.get(name)
        if skill is None:
            return json.dumps({"error": f"Unknown skill '{name}'"})
        return skill.content
