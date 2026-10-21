"""Server wiring and entry point."""

from __future__ import annotations

from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, AuthProvider

from tc_mcp import config
from tc_mcp import prompts as prompt_modules
from tc_mcp import resources as resource_modules
from tc_mcp.repository import Repository
from tc_mcp.tools import authoring, discovery, export, planning, quality, search

INSTRUCTIONS = (
    "TestCreator MCP (TC MCP) gives you read access to 5,000 VWO test cases. "
    "Use list_modules and get_filter_options first to learn the catalog, "
    "search_test_cases to filter (by module, priority, type, browser, device, status), "
    "get_top_tests_for_module to rank what to run first, and build_test_suite for "
    "smoke/sanity/regression suites. There are also quality, authoring and export tools."
)


class StaticTokenAuth(AuthProvider):
    """Accept a single fixed bearer token for HTTP mode."""

    def __init__(self, token: str):
        super().__init__()
        self._token = token

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if token == self._token:
            return AccessToken(token=token, client_id="tc-mcp", scopes=[])
        return None


def create_server(
    data_path: Optional[str] = None,
    overlay_path: Optional[str] = None,
    allow_write: Optional[bool] = None,
) -> FastMCP:
    data_path = data_path or config.DATA_PATH
    overlay_path = overlay_path or config.OVERLAY_PATH
    if allow_write is None:
        allow_write = config.ALLOW_WRITE

    repo = Repository(data_path, overlay_path)

    mcp = FastMCP(
        "tc-mcp",
        instructions=INSTRUCTIONS,
    )

    discovery.register(mcp, repo)
    search.register(mcp, repo)
    planning.register(mcp, repo)
    quality.register(mcp, repo)
    authoring.register(mcp, repo, allow_write)
    export.register(mcp, repo)
    resource_modules.register(mcp, repo)
    prompt_modules.register(mcp)

    return mcp


def main() -> None:
    mcp = create_server()

    transport = config.TRANSPORT.lower()
    if transport in {"http", "streamable-http"}:
        if config.AUTH_TOKEN:
            mcp.auth = StaticTokenAuth(config.AUTH_TOKEN)
        mcp.run(transport="http", host="0.0.0.0", port=config.PORT)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
