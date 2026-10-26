"""Repository tests: catalog size, format, provenance, categories."""

from __future__ import annotations


def test_at_least_50_skills(repo):
    assert len(repo.all()) >= 50
    assert len(repo.all()) == 60


def test_provenance_split(repo):
    upstream = [s for s in repo.all() if s.provenance == "upstream"]
    local = [s for s in repo.all() if s.provenance == "local"]
    assert len(upstream) == 36
    assert len(local) == 24


def test_unique_names(repo):
    names = [s.name for s in repo.all()]
    assert len(names) == len(set(names))


def test_every_skill_has_valid_format(repo):
    for s in repo.all():
        assert s.name, f"{s.path} has no name"
        assert s.description, f"{s.name} has no description"
        body = s.body
        assert "When to use" in body, f"{s.name} missing 'When to use'"
        assert "Workflow" in body, f"{s.name} missing 'Workflow'"
        assert "Output" in body, f"{s.name} missing 'Output'"
        assert "Guardrails" in body, f"{s.name} missing 'Guardrails'"


def test_expected_categories(repo):
    categories = [c["category"] for c in repo.categories()]
    for expected in [
        "Playwright",
        "Selenium",
        "Cypress",
        "API Testing",
        "Performance",
        "Security",
        "LLM Evaluation",
        "AI Agents",
        "MCP",
        "STLC · Test Planning",
        "STLC · Test Case Development",
        "STLC · Defect Management",
    ]:
        assert expected in categories, f"missing category {expected}"


def test_stats(repo):
    stats = repo.stats()
    assert stats["total_skills"] == 60
    assert stats["categories"] >= 12


def test_get_known_and_unknown(repo):
    skill = repo.get("test-case-writer")
    assert skill is not None
    assert skill.name == "test-case-writer"
    assert repo.get("does-not-exist") is None


def test_get_is_case_insensitive(repo):
    assert repo.get("PW-API-TESTER").name == "pw-api-tester"
