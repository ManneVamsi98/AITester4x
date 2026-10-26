"""Keyword search over the skill catalog.

The search is deliberately dependency-free (beyond stdlib) and deterministic:
it tokenizes, singularizes, and expands synonyms on both the query and the
skill text, then scores a skill per query token by the best field that token
matched (name > description > category/area > body). Synonym groups cover the
authoring verbs ("creator", "writer", "generator", "builder", "designer",
"scripter"), framework abbreviations ("pw" == "playwright", "se" ==
"selenium", "cy" == "cypress"), and a few testing-domain equivalences
("bug" == "defect").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from tsf_mcp.models import Skill

_WORD_RE = re.compile(r"[a-z0-9]+")

# Groups of tokens that should match one another. Membership is symmetric:
# any token in a group expands to the whole group on both sides.
_SYNONYM_SETS: list[frozenset[str]] = [
    # Authoring verbs: "test case creator" must match "test-case-writer".
    frozenset(
        {
            "create", "creates", "creating", "created", "creator", "creators",
            "generate", "generates", "generating", "generator", "generators",
            "write", "writes", "writing", "writer", "writers",
            "build", "builds", "building", "builder", "builders",
            "design", "designs", "designing", "designer", "designers",
            "author", "authors", "authoring", "script", "scripter",
        }
    ),
    # Framework abbreviations.
    frozenset({"playwright", "pw", "playright"}),
    frozenset({"selenium", "se"}),
    frozenset({"cypress", "cy"}),
    # Defect == bug.
    frozenset({"bug", "bugs", "defect", "defects"}),
]

# Compound words that should also match as their parts.
_COMPOUNDS: dict[str, list[str]] = {
    "testcase": ["test", "case"],
    "testcases": ["test", "case"],
    "testcasecreator": ["test", "case", "creator"],
    "testplan": ["test", "plan"],
    "testplans": ["test", "plan"],
    "testplanning": ["test", "plan"],
    "loadtest": ["load", "test"],
    "loadtesting": ["load", "test"],
    "testdata": ["test", "data"],
    "testbug": ["test", "bug"],
}

_INDEX: dict[str, frozenset[str]] = {}
for _group in _SYNONYM_SETS:
    for _token in _group:
        _INDEX[_token] = _group


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def singularize(word: str) -> str:
    """A small, domain-focused English singularizer (plus -ing stripping)."""
    if len(word) <= 3:
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"  # strategies -> strategy
    if word.endswith("sses"):
        return word[:-2]  # classes -> class, processes -> process
    if word.endswith(("xes", "ches", "shes", "zes")):
        return word[:-2]
    if word.endswith("ses"):
        return word[:-1]  # cases -> case
    if word.endswith("ing") and len(word) > 4:
        stem = word[:-3]
        if stem.endswith(stem[-1]):
            stem = stem[:-1]  # running -> run
        if len(stem) >= 3:
            return stem  # testing -> test
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]  # bugs -> bug, tests -> test
    return word


def expand_token(token: str) -> frozenset[str]:
    """Return the set of tokens that a single token is equivalent to."""
    out = {token}
    singular = singularize(token)
    out.add(singular)

    group = _INDEX.get(token) or _INDEX.get(singular)
    if group is not None:
        out |= group

    for extra in _COMPOUNDS.get(token, _COMPOUNDS.get(singular, [])):
        out.add(extra)

    return frozenset(out)


def expand_tokens(tokens: list[str]) -> frozenset[str]:
    out: set[str] = set()
    for token in tokens:
        out |= expand_token(token)
    return frozenset(out)


@dataclass
class SearchHit:
    skill: Skill
    score: float
    matched: list[str]


@dataclass
class SearchIndex:
    skills: list[Skill] = field(default_factory=list)
    _name: dict[str, frozenset[str]] = field(default_factory=dict)
    _description: dict[str, frozenset[str]] = field(default_factory=dict)
    _meta: dict[str, frozenset[str]] = field(default_factory=dict)
    _body: dict[str, frozenset[str]] = field(default_factory=dict)

    def add(self, skill: Skill) -> None:
        self.skills.append(skill)
        self._name[skill.name] = expand_tokens(tokenize(skill.name))
        self._description[skill.name] = expand_tokens(tokenize(skill.description))
        meta_text = (
            f"{skill.category} {skill.area} "
            f"{' '.join(skill.metadata.values()) if isinstance(skill.metadata, dict) else ''}"
        )
        self._meta[skill.name] = expand_tokens(tokenize(meta_text))
        self._body[skill.name] = expand_tokens(tokenize(skill.body))

    def _score_one(self, skill: Skill, raw_tokens: list[str]) -> tuple[float, list[str]]:
        name = self._name[skill.name]
        description = self._description[skill.name]
        meta = self._meta[skill.name]
        body = self._body[skill.name]

        score = 0.0
        matched: list[str] = []
        for token in raw_tokens:
            expanded = expand_token(token)
            if expanded & name:
                score += 8.0
                if "name" not in matched:
                    matched.append("name")
            elif expanded & description:
                score += 4.0
                if "description" not in matched:
                    matched.append("description")
            elif expanded & meta:
                score += 2.0
                if "category/area" not in matched:
                    matched.append("category/area")
            elif expanded & body:
                score += 1.0
                if "body" not in matched:
                    matched.append("body")

        # Exact-name match is a strong signal.
        normalized_name = re.sub(r"[^a-z0-9]+", "", skill.name.lower())
        normalized_query = re.sub(r"[^a-z0-9]+", "", " ".join(raw_tokens).lower())
        if normalized_query and normalized_query == normalized_name:
            score += 20.0
            if "name" not in matched:
                matched.append("name")

        return score, matched

    def search(
        self,
        query: str,
        category: str | None = None,
        area: str | None = None,
        provenance: str | None = None,
    ) -> list[SearchHit]:
        raw_tokens = tokenize(query)

        hits: list[SearchHit] = []
        for skill in self.skills:
            if category is not None and skill.category.lower() != category.lower():
                continue
            if area is not None and skill.area.lower() != area.lower():
                continue
            if provenance is not None and skill.provenance != provenance:
                continue

            score, matched = self._score_one(skill, raw_tokens)
            if score > 0:
                hits.append(SearchHit(skill=skill, score=score, matched=matched))

        # Rank by score desc, then by name for a stable, repeatable order.
        hits.sort(key=lambda h: (-h.score, h.skill.name))
        return hits
