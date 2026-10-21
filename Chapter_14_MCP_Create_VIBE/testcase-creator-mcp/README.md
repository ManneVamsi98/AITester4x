# TestCreator MCP (TC MCP)

A [FastMCP](https://gofastmcp.com) server that turns a CSV of **5,000 VWO test cases**
into 21 tools any MCP client can call (Claude Code, Claude Desktop, Cursor, VS Code).
QA and devs can find tests by module and priority, rank the top tests to run, build
smoke/sanity/regression suites, spot duplicates and coverage gaps, write new tests in
the same VWO format, and export to CSV / Jira CSV / Markdown / Gherkin.

The server makes **no LLM calls** — it is deterministic, free and offline. The client's
LLM does the reasoning; TC MCP supplies the data, ranking, validation and templates.

## Requirements

- Python 3.11 – 3.14
- [uv](https://docs.astral.sh/uv/) (or plain `pip`)

## Install and run

```bash
cd testcase-creator-mcp
uv sync                 # creates .venv and installs fastmcp
uv run tc-mcp           # starts the stdio server
```

The source CSV is bundled into the package at `src/tc_mcp/data/vwo_5000_test_cases.csv`,
so `uvx` installs work with no repo checkout needed.

## Connection options

### A. Local stdio

```bash
claude mcp add tc-mcp -- uv run --directory "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testcase-creator-mcp" tc-mcp
```

Claude Desktop / Cursor (`mcpServers` block):

```json
{
  "mcpServers": {
    "tc-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testcase-creator-mcp", "tc-mcp"],
      "env": { "TC_MCP_ALLOW_WRITE": "false" }
    }
  }
}
```

VS Code (`.vscode/mcp.json`):

```json
{
  "servers": {
    "tc-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "E:/AI/AI Tester 4x/AI Tester 4x/Chapter_14_MCP_Create_VIBE/testcase-creator-mcp", "tc-mcp"]
    }
  }
}
```

### B. `uvx` from git (nothing to clone)

```bash
claude mcp add tc-mcp -- uvx --from "git+https://github.com/<org>/<repo>#subdirectory=chapter_14_MCP_Create_VIBE/testcase-creator-mcp" tc-mcp
```

### C. Hosted HTTP (shared server)

```bash
# on the server / VM / Docker
TC_MCP_TRANSPORT=http TC_MCP_PORT=8000 TC_MCP_AUTH_TOKEN=secret tc-mcp

# on the client
claude mcp add --transport http tc-mcp http://<host>:8000/mcp --header "Authorization: Bearer secret"
```

The MCP Inspector can point at the HTTP server with:

```bash
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8000/mcp
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TC_MCP_DATA_PATH` | bundled CSV | Point at a different or newer CSV |
| `TC_MCP_OVERLAY_PATH` | `data/tc_additions.csv` | Where new and edited tests go |
| `TC_MCP_ALLOW_WRITE` | `false` | Turns on `add_test_cases` and `update_test_case` |
| `TC_MCP_EXPORT_DIR` | `./exports` | Where large exports are written |
| `TC_MCP_TRANSPORT` | `stdio` | Set to `http` for a shared server |
| `TC_MCP_PORT` | `8000` | HTTP port |
| `TC_MCP_AUTH_TOKEN` | unset | Bearer token, required in HTTP mode |

Read-only is the default: with writes off, the two write tools are not even registered.

## Tools (21)

- **Discovery** — `list_modules`, `get_filter_options`, `get_test_stats`
- **Find and fetch** — `get_test_case`, `search_test_cases`, `search_by_keyword`,
  `get_top_tests_for_module`, `get_similar_test_cases`
- **Execution planning** — `build_test_suite`, `get_browser_device_matrix`,
  `get_automation_candidates`, `estimate_execution_effort`
- **Quality** — `find_duplicate_tests`, `find_coverage_gaps`, `validate_test_case`
- **Authoring** — `get_test_case_template`, `add_test_cases` (write),
  `update_test_case` (write)
- **Export** — `export_test_cases`, `convert_to_gherkin`, `generate_automation_stub`

There are also **4 resources** (`tc://schema`, `tc://modules`, `tc://stats/summary`,
`tc://test/{key}`) and **3 prompts** (`generate_test_cases`, `plan_release_run`,
`review_module_coverage`).

## The data

- 5,000 rows, `VWO-1001` to `VWO-6000`
- 17 modules, 72 features, 1,520 scenarios
- Priorities: Highest 396 · High 1,546 · Medium 2,198 · Low 860
- 4,585 live tests (415 deprecated are hidden by default)
- 466 flagged duplicate rows

Loading fixes three source-CSV quirks without editing it: broken `A/B Testing` labels
(saved as `a`), doubled `regression` labels, and duplicate detection. Writes go to a
separate `tc_additions.csv` overlay, so the source CSV is never changed.

## Run the tests

```bash
uv run pytest
```
