---
name: mcp-server-builder
description: >-
  Builds a Model Context Protocol (MCP) server that exposes tools, resources, and prompts
  to any LLM client. Use when a tester says "build an MCP server", "create an MCP tool",
  "expose this data over MCP", or wants a local or streamable MCP server. Produces a
  FastMCP or TypeScript MCP server skeleton with tools and a connection string.
license: MIT
metadata:
  author: TheTestingAcademy
  area: mcp
  version: 1.0.0
---

# MCP Server Builder

You build **MCP servers** that let any LLM client call your tools, read your resources,
and use your prompts. You keep the server deterministic and let the client's LLM do the
reasoning.

## When to use
- A capability or dataset should be exposed to LLM clients.
- Someone says "build an MCP server", "create an MCP tool", "expose this over MCP".
- A team wants a shared tool usable from Claude Code, Cursor, or VS Code.

## Workflow
1. **Decide the surface.** List the tools (actions), resources (read-only data), and
   prompts (reusable workflows) the client needs. One clear job per tool.
2. **Choose the framework.** FastMCP (Python) or the TypeScript MCP SDK, matching the
   team's stack. Keep dependencies light.
3. **Write the tools.** Give each a schema with typed params, and a docstring that opens
   with *when to use it*. Return structured, deterministic results — no LLM calls inside.
4. **Wire transport.** Support stdio for local use and streamable HTTP for sharing, with
   the connection string documented.
5. **HUMAN REVIEW GATE (mandatory).** Verify the server lists and calls every tool before
   handing it to teammates.

## Output shape
```python
from fastmcp import FastMCP
mcp = FastMCP("my-mcp", instructions="...")

@mcp.tool
def search(query: str) -> list[dict]:
    """Find items matching a keyword. Use when a user wants to search the catalog."""
    return [item for item in CATALOG if query.lower() in item["name"]]

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Guardrails
- No LLM calls inside the server — keep it deterministic, free, and offline.
- Every tool needs a clear *when to use* description or the client's LLM picks wrong.
- Support both stdio and HTTP transports; document the connection string.
- The server is a draft until verified with the MCP Inspector or a client.
