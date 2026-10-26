# Test Skill Finder MCP (TSF MCP)

A [FastMCP](https://gofastmcp.com) server that exposes a catalog of **60 testing
skills** as searchable tools any MCP client can call (Claude Code, Claude Desktop,
Cursor, VS Code). The skills cover the full Software Testing Life Cycle plus the
automation stacks: STLC, Playwright, Selenium, Cypress, API testing, performance,
security, LLM evaluation, AI agents, MCP, and automation.

The `/skills` folder is the **source of truth** — every skill is a folder with a
`SKILL.md` (YAML frontmatter + instructions), in the same format as the upstream
[skillmasterclass](https://github.com/PramodDutta/skillmasterclass) repository.

The server makes **no LLM calls**: it is deterministic, free and offline. The
client's LLM does the reasoning; TSF MCP finds the right skill and hands over its
full instructions.

## Requirements

- Python 3.11 – 3.14
- [uv](https://docs.astral.sh/uv/) (or plain `pip`)

## Install and run

```bash
cd testskill-finder-mcp
uv sync          # creates .venv and installs fastmcp + pyyaml
uv run tsf-mcp   # starts the stdio server
```

The `/skills` folder is bundled into the package (`tsf_mcp/data/skills`), so `uvx`
installs work with no repo checkout needed.

## Connection options

### A. Local stdio

```bash
claude mcp add tsf-mcp -- uv run --directory "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testskill-finder-mcp" tsf-mcp
```

Claude Desktop / Cursor (`mcpServers` block):

```json
{
  "mcpServers": {
    "tsf-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testskill-finder-mcp", "tsf-mcp"]
    }
  }
}
```

VS Code (`.vscode/mcp.json`):

```json
{
  "servers": {
    "tsf-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testskill-finder-mcp", "tsf-mcp"]
    }
  }
}
```

### B. `uvx` from git (nothing to clone)

```bash
claude mcp add tsf-mcp -- uvx --from "git+https://github.com/<org>/<repo>#subdirectory=chapter_14_MCP_Create_VIBE/testskill-finder-mcp" tsf-mcp
```

### C. Hosted streamable HTTP (shared server)

```bash
# on the server / VM / Docker
TSF_MCP_TRANSPORT=http TSF_MCP_PORT=8000 TSF_MCP_AUTH_TOKEN=secret tsf-mcp

# on the client
claude mcp add --transport http tsf-mcp http://<host>:8000/mcp --header "Authorization: Bearer secret"
```

The MCP Inspector can point at the HTTP server with:

```bash
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8000/mcp
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TSF_MCP_SKILLS_PATH` | bundled `/skills` | Point at a different skills folder |
| `TSF_MCP_TRANSPORT` | `stdio` | Set to `http` for a shared server |
| `TSF_MCP_PORT` | `8000` | HTTP port |
| `TSF_MCP_AUTH_TOKEN` | unset | Bearer token, required in HTTP mode |
| `TSF_MCP_ALLOW_SYNC` | `true` | Turns on the `sync_skills` write tool |
| `TSF_MCP_UPSTREAM_REPO` | skillmasterclass git URL | Where `sync_skills` pulls from |

## Tools (7)

- **Find** — `search_skills` (keyword search), `get_skill` (full SKILL.md),
  `get_skill_summary` (metadata only), `list_skills` (browse/filter),
  `list_categories` (groups + counts), `suggest_skills` (did-you-mean)
- **Admin** — `sync_skills` (re-download upstream skills)

Example searches: "playwright" → the Playwright pack; "playwright api" →
`pw-api-tester`; "test case creator" → `test-case-writer`; "test plan creator" →
`test-plan-generator`; "bug strategy" → `bug-reporter`.

## Resources (4)

`tsf://catalog`, `tsf://categories`, `tsf://stats`, and `tsf://skill/{name}` (a
resource template so a client can @-mention a single skill).

## Prompts (4)

`find_skill`, `use_skill`, `recommend_skill`, and `explore_category` — reusable
workflows that guide the client's LLM to search, read, and apply a skill.

## The skills (60)

- **36 upstream** skills synced from the skillmasterclass repo:
  14 STLC skills, 11 Playwright, 11 Selenium.
- **24 local** skills added in the same format: Cypress (5), API (4), Performance
  (3), Security (3), LLM evaluation (3), AI agents (2), MCP (3), Automation (1).

See [`skills/CATALOG.md`](skills/CATALOG.md) for the full list grouped by category.

## Run the tests

```bash
uv run pytest
```
