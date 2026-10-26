"""Prompts: reusable workflows a user picks from the client menu."""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.prompt(
        description="Find the right skill for a topic or testing task, then read and summarize it."
    )
    def find_skill(query: str) -> str:
        return (
            f"Find the best testing skill for: '{query}'.\n\n"
            "1. Call search_skills with the query to get ranked matches.\n"
            "2. If nothing matches, call suggest_skills for 'did you mean' corrections.\n"
            "3. Pick the top match and call get_skill on its name to read the full instructions.\n"
            "4. Summarize what the skill does, when to use it, and its workflow in 3-5 lines.\n"
            "If several skills are relevant, list them and say which one fits best and why."
        )

    @mcp.prompt(
        description="Read a specific skill and apply its workflow to the current task."
    )
    def use_skill(name: str) -> str:
        return (
            f"Use the skill named '{name}'.\n\n"
            "1. Call get_skill with that name to read its full instructions.\n"
            "2. Follow its Workflow section step by step.\n"
            "3. Produce output in its Output shape format.\n"
            "4. Respect its Guardrails, including any mandatory human-review gate.\n"
            "Do not skip steps or fabricate anything the skill says to confirm first."
        )

    @mcp.prompt(
        description="Recommend the best skill(s) for a described testing task."
    )
    def recommend_skill(task: str) -> str:
        return (
            f"Recommend the best testing skill(s) for this task: '{task}'.\n\n"
            "1. Call list_categories to understand the catalog.\n"
            "2. Call search_skills with a keyword that captures the task.\n"
            "3. Compare the top matches and recommend one primary skill plus a fallback.\n"
            "4. Explain your recommendation and suggest the next skill to chain after it "
            "(e.g. test-plan-generator -> test-case-writer -> automation-script-generator)."
        )

    @mcp.prompt(
        description="Browse a category and describe the skills it contains and how they chain together."
    )
    def explore_category(category: str) -> str:
        return (
            f"Explore the '{category}' category of testing skills.\n\n"
            "1. Call list_skills with the category to see every skill in it.\n"
            "2. Summarize each skill in one line.\n"
            "3. Explain how the skills chain together into a workflow.\n"
            "4. Note which skill a beginner should start with."
        )
