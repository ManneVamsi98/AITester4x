"""MCP tools: find, search, list, get, suggest, and sync skills."""

from __future__ import annotations

from typing import Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from tsf_mcp import config
from tsf_mcp.repository import Repository
from tsf_mcp.sync import sync_upstream


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, config.MAX_RESULTS))


def register(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "Find skills by keyword. This is the main search tool. Use it when a user "
            "asks for a skill about a topic or tool, e.g. 'playwright', 'playwright api', "
            "'test case creator', 'test plan', 'bug strategy', 'selenium', 'cypress', "
            "'api testing', 'performance', 'security'. Returns ranked matches with a score "
            "and the fields that matched. For the full content of one skill, call get_skill "
            "with the name this returns. Use list_categories to see valid category filters."
        ),
    )
    def search_skills(
        query: str,
        category: Optional[str] = None,
        provenance: Optional[Literal["upstream", "local"]] = None,
        limit: int = config.DEFAULT_LIMIT,
    ) -> dict:
        limit = _clamp_limit(limit)
        rows = repo.search(query, category=category, provenance=provenance, limit=limit)
        suggestions: list[str] = []
        if not rows:
            suggestions = repo.suggest(query, limit=5)["did_you_mean"]
        return {
            "query": query,
            "total_matched": len(rows),
            "returned": len(rows),
            "results": rows,
            "suggestions": suggestions,
        }

    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "Return the full SKILL.md content of one skill by its name. Use this after "
            "search_skills or list_skills to read a skill's complete instructions, workflow, "
            "output shape and guardrails so you can actually follow it. For just the metadata "
            "without the full body, use get_skill_summary."
        ),
    )
    def get_skill(name: str) -> dict:
        skill = repo.get(name)
        if skill is None:
            raise ToolError(
                f"Unknown skill '{name}'. Use search_skills to find a skill, "
                f"or list_skills to list them all."
            )
        return skill.to_detail()

    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "Return the summary metadata of one skill (name, description, category, area, "
            "provenance, path) without the full body. Use it to quickly compare skills "
            "before reading the full content with get_skill."
        ),
    )
    def get_skill_summary(name: str) -> dict:
        skill = repo.get(name)
        if skill is None:
            raise ToolError(f"Unknown skill '{name}'. Use search_skills or list_skills.")
        return skill.to_summary()

    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "List skills, optionally filtered by category or provenance. Use it to browse "
            "the whole catalog or a single group (e.g. category='Playwright'). Returns a "
            "paginated envelope with total and offset. Use list_categories to see the valid "
            "category names."
        ),
    )
    def list_skills(
        category: Optional[str] = None,
        provenance: Optional[Literal["upstream", "local"]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        limit = _clamp_limit(limit)
        offset = max(0, offset)
        skills = repo.all()
        if category is not None:
            skills = [s for s in skills if s.category.lower() == category.lower()]
        if provenance is not None:
            skills = [s for s in skills if s.provenance == provenance]

        page = skills[offset : offset + limit]
        return {
            "total_matched": len(skills),
            "returned": len(page),
            "offset": offset,
            "results": [s.to_summary() for s in page],
        }

    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "List every category with its skill count and the names in it. Use this first "
            "to learn the catalog, or to find the valid category values for search_skills "
            "and list_skills."
        ),
    )
    def list_categories() -> dict:
        return {
            "categories": repo.categories(),
            "stats": repo.stats(),
        }

    @mcp.tool(
        tags={"find"},
        annotations={"readOnlyHint": True},
        description=(
            "Suggest skills for a query that may be misspelled or off the mark. Returns "
            "'did_you_mean' name corrections plus related skills. Use it when search_skills "
            "returns nothing or few results."
        ),
    )
    def suggest_skills(query: str, limit: int = 5) -> dict:
        return repo.suggest(query, limit=max(1, min(limit, 20)))

    @mcp.tool(
        tags={"admin"},
        description=(
            "Re-download the upstream skills from the skillmasterclass repository into the "
            "local /skills folder and refresh the catalog. Use this to pull newer or "
            "additional upstream skills. The /skills folder is the source of truth and is "
            "committed; this tool mutates it, so call it only when a refresh is wanted."
        ),
    )
    def sync_skills() -> dict:
        if not config.ALLOW_SYNC:
            raise ToolError("Syncing is disabled (TSF_MCP_ALLOW_SYNC=false).")
        summary = sync_upstream(repo.skills_dir)
        repo.reload()
        return {**summary, "stats": repo.stats()}
