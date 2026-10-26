"""Server wiring and entry point."""

from __future__ import annotations

from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, AuthProvider

from tsf_mcp import config
from tsf_mcp import prompts as prompt_modules
from tsf_mcp import resources as resource_modules
from tsf_mcp.repository import Repository
from tsf_mcp.tools import register as register_tools

INSTRUCTIONS = (
    "Test Skill Finder MCP (tsf-mcp) lets you find testing skills from a catalog of "
    "50+ skills (STLC, Playwright, Selenium, Cypress, API, performance, security, "
    "LLM evaluation, AI agents, MCP, automation). Use search_skills to find a skill "
    "by keyword ('playwright', 'test case creator', 'test plan', 'bug strategy'), "
    "get_skill to read a skill's full instructions, list_categories to browse, and "
    "suggest_skills when a query misses. The /skills folder is the source of truth."
)


class StaticTokenAuth(AuthProvider):
    """Accept a single fixed bearer token for HTTP mode."""

    def __init__(self, token: str):
        super().__init__()
        self._token = token

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if token == self._token:
            return AccessToken(token=token, client_id="tsf-mcp", scopes=[])
        return None


def create_server(skills_dir: Optional[str] = None) -> FastMCP:
    repo = Repository(skills_dir)

    mcp = FastMCP("tsf-mcp", instructions=INSTRUCTIONS)

    register_tools(mcp, repo)
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
