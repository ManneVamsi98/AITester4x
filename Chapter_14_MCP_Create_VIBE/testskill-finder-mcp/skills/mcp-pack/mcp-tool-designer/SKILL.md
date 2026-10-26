---
name: mcp-tool-designer
description: >-
  Designs MCP tools with clear names, typed schemas, and "when to use" descriptions so a
  client LLM picks the right tool. Use when a tester says "design an MCP tool", "write
  tool descriptions", "make the LLM pick the right tool", or wants tools that are easy to
  call correctly. Produces tool specs with schemas, examples, and disambiguation rules.
license: MIT
metadata:
  author: TheTestingAcademy
  area: mcp
  version: 1.0.0
---

# MCP Tool Designer

You design **MCP tools the client's LLM will pick correctly**. A tool is only useful if
the LLM calls the right one, with the right arguments, at the right time — and that
depends almost entirely on the name, schema, and description.

## When to use
- New MCP tools need to be designed or existing ones confuse the client.
- Someone says "design the tool", "write good tool descriptions", "fix tool selection".
- A server has overlapping tools and the LLM keeps calling the wrong one.

## Workflow
1. **Define one job per tool.** A tool does one thing well. Split overlapping tools;
   merge tools that differ only by a filter parameter.
2. **Name by action.** Use `verb_noun` (`search_skills`, `get_skill`) so intent is
   obvious at a glance.
3. **Type the schema.** Use specific types and enums/literals for bounded values so the
   LLM stops guessing. Add clear defaults and limits.
4. **Write the description.** Open with *when to use it*, then name the sibling tool to use
   instead for related jobs. Give one concrete example.
5. **HUMAN REVIEW GATE (mandatory).** Verify with a real client that the intended tool is
   selected for representative questions.

## Output shape
```python
@mcp.tool
def search_skills(query: str, limit: int = 10) -> list[dict]:
    """Find skills matching a keyword. Use when a user wants to discover which skill
    covers a topic (e.g. "playwright", "test plan"). For a single skill's full content,
    use get_skill with the name this returns. limit is 1-50."""
```

## Guardrails
- Do not create tools with overlapping jobs — they confuse the LLM's choice.
- Every description must say *when to use* and which sibling tool to use instead.
- Use enums/literals in schemas; a free-form string invites bad arguments.
- Validate selection against real questions before shipping the tool.
