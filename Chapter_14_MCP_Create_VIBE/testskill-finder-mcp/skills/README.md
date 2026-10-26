# Skills folder

This folder is the **source of truth** for the Test Skill Finder MCP: **60 skills** (36 synced from the upstream [skillmasterclass](https://github.com/PramodDutta/skillmasterclass) repo, 24 local). Every skill is a folder containing a `SKILL.md`.

## Skill format

Each `SKILL.md` has YAML frontmatter followed by the instructions:

```yaml
---
name: <skill-name>
description: >-
  <what it does, with "Use when" trigger phrases>
license: MIT
metadata:
  author: TheTestingAcademy
  <pack|stlc-phase|area>: <tag>
  version: 1.0.0
---
```

The body has four sections: **When to use**, **Workflow**, **Output shape**, and **Guardrails** (many end in a mandatory human-review gate).

## Categories

- **AI Agents** — 2 skills
- **API Testing** — 4 skills
- **Automation** — 1 skills
- **Cypress** — 5 skills
- **LLM Evaluation** — 3 skills
- **MCP** — 3 skills
- **Performance** — 3 skills
- **Playwright** — 11 skills
- **STLC · Defect Management** — 3 skills
- **STLC · Requirement Analysis** — 1 skills
- **STLC · Test Case Development** — 2 skills
- **STLC · Test Closure** — 2 skills
- **STLC · Test Design** — 2 skills
- **STLC · Test Execution** — 3 skills
- **STLC · Test Planning** — 1 skills
- **Security** — 3 skills
- **Selenium** — 11 skills

See [`CATALOG.md`](CATALOG.md) for the full list of every skill.

