"""Tool/resource/prompt tests through the in-memory FastMCP client."""

from __future__ import annotations

import pytest


def test_tools_registered(tool_names):
    for expected in [
        "search_skills",
        "get_skill",
        "get_skill_summary",
        "list_skills",
        "list_categories",
        "suggest_skills",
        "sync_skills",
    ]:
        assert expected in tool_names, f"missing tool {expected}"
    assert len(tool_names) == 7


def test_search_skills_tool(call_tool):
    data = call_tool("search_skills", {"query": "playwright api"}).data
    assert data["total_matched"] >= 1
    assert data["results"][0]["name"] == "pw-api-tester"
    assert "score" in data["results"][0]


def test_search_skills_category_filter(call_tool):
    data = call_tool("search_skills", {"query": "test", "category": "Cypress"}).data
    assert all(r["category"] == "Cypress" for r in data["results"])


def test_get_skill_tool(call_tool):
    data = call_tool("get_skill", {"name": "test-case-writer"}).data
    assert data["name"] == "test-case-writer"
    assert "Workflow" in data["content"]
    assert data["provenance"] == "upstream"


def test_get_skill_summary_tool(call_tool):
    data = call_tool("get_skill_summary", {"name": "cy-test-generator"}).data
    assert data["name"] == "cy-test-generator"
    assert "content" not in data


def test_get_skill_unknown_raises(call_tool):
    with pytest.raises(Exception):
        call_tool("get_skill", {"name": "nope"})


def test_list_skills_tool(call_tool):
    data = call_tool("list_skills", {"category": "Playwright"}).data
    assert data["total_matched"] == 11
    assert all(r["category"] == "Playwright" for r in data["results"])


def test_list_categories_tool(call_tool):
    data = call_tool("list_categories", {}).data
    assert data["stats"]["total_skills"] == 60
    categories = [c["category"] for c in data["categories"]]
    assert "Playwright" in categories
    assert "Cypress" in categories


def test_suggest_skills_tool(call_tool):
    data = call_tool("suggest_skills", {"query": "playwrght"}).data
    assert data["did_you_mean"] or data["related"]


def test_prompts_registered(prompt_names):
    for expected in ["find_skill", "use_skill", "recommend_skill", "explore_category"]:
        assert expected in prompt_names, f"missing prompt {expected}"
    assert len(prompt_names) == 4


def test_resources_registered(resource_uris):
    for expected in ["tsf://catalog", "tsf://categories", "tsf://stats"]:
        assert expected in resource_uris, f"missing resource {expected}"


def test_resource_templates_registered(resource_template_uris):
    assert "tsf://skill/{name}" in resource_template_uris
