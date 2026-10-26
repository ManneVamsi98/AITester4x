"""Search tests: the golden queries from the objective."""

from __future__ import annotations


def _top_name(repo, query, **kwargs):
    rows = repo.search(query, **kwargs)
    assert rows, f"no results for '{query}'"
    return rows[0]["name"]


def test_search_playwright(repo):
    name = _top_name(repo, "playwright")
    assert name.startswith("pw-"), f"expected a playwright skill, got {name}"


def test_search_playwright_api(repo):
    name = _top_name(repo, "playwright api")
    assert name == "pw-api-tester"


def test_search_test_case_creator(repo):
    name = _top_name(repo, "test case creator")
    assert name == "test-case-writer"


def test_search_test_plan_creator(repo):
    name = _top_name(repo, "test plan creator")
    assert name == "test-plan-generator"


def test_search_bug_strategy(repo):
    name = _top_name(repo, "bug strategy")
    assert name in {"bug-reporter", "bug-triage-assistant", "rca-analyzer"}


def test_search_selenium(repo):
    name = _top_name(repo, "selenium")
    assert name.startswith("se-"), f"expected a selenium skill, got {name}"


def test_search_cypress(repo):
    name = _top_name(repo, "cypress")
    assert name.startswith("cy-"), f"expected a cypress skill, got {name}"


def test_search_api_testing(repo):
    name = _top_name(repo, "api testing")
    assert "api" in name, f"expected an api skill, got {name}"


def test_search_security(repo):
    name = _top_name(repo, "security")
    assert name in {
        "security-threat-modeler",
        "owasp-top10-checker",
        "injection-tester",
    }


def test_search_synonym_creator_writer(repo):
    # "creator" and "writer" are synonyms via the authoring group.
    a = _top_name(repo, "test case writer")
    b = _top_name(repo, "test case generator")
    assert a == "test-case-writer"
    assert b == "test-case-writer"


def test_results_have_score_and_matched(repo):
    rows = repo.search("playwright api")
    assert all("score" in r and "matched_fields" in r for r in rows)


def test_suggest_did_you_mean(repo):
    result = repo.suggest("playwrght", limit=5)
    assert "playwright" in result["did_you_mean"] or any(
        "pw-" in r["name"] for r in result["related"]
    )
