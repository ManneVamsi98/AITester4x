---
name: mcp-client-connector
description: >-
  Writes MCP client connection configs for Claude Code, Claude Desktop, Cursor, and VS
  Code. Use when a tester says "connect this MCP", "add this MCP server to Claude",
  "write the mcpServers config", or wants the exact connection string for stdio or HTTP.
  Produces ready-to-paste client configs and the run commands.
license: MIT
metadata:
  author: TheTestingAcademy
  area: mcp
  version: 1.0.0
---

# MCP Client Connector

You write the **exact config a client needs to connect** to an MCP server — the right
command, args, and env for stdio, or the URL and headers for streamable HTTP. A server is
useless if no one can connect to it.

## When to use
- An MCP server needs to be connected to a client.
- Someone says "connect this MCP", "add the server to Claude", "write the config".
- A teammate needs the exact connection string for their editor.

## Workflow
1. **Identify the transport.** stdio (a local command) or streamable HTTP (a URL). Pick
   the right one for local vs shared use.
2. **Write the config.** For stdio, give the command, args, and any env. For HTTP, give
   the URL and any `Authorization` header.
3. **Cover each client.** Claude Code (`claude mcp add`), Claude Desktop / Cursor
   (`mcpServers` JSON), and VS Code (`.vscode/mcp.json` `servers` key).
4. **Include the run command.** Show how to start the server and how to verify it lists
   tools (Inspector or a quick client call).
5. **HUMAN REVIEW GATE (mandatory).** Confirm the paths, ports, and tokens are correct for
   the actual machine before sharing.

## Output shape
```bash
claude mcp add my-mcp -- uv run --directory /abs/path my-mcp
```
```json
{
  "mcpServers": {
    "my-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/abs/path", "my-mcp"]
    }
  }
}
```

## Guardrails
- Never share a real token or secret in a config — use a placeholder and env var.
- Use absolute paths and correct commands; a wrong path is the top connection failure.
- Match the config schema to the exact client (they differ between Claude and VS Code).
- Verify the server lists tools before declaring it connected.
