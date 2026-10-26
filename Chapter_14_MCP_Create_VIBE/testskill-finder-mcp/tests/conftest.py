"""Shared fixtures for the Test Skill Finder MCP test suite."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastmcp import Client

from tsf_mcp.repository import Repository
from tsf_mcp.server import create_server

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


@pytest.fixture(scope="session")
def repo() -> Repository:
    return Repository(SKILLS_DIR)


@pytest.fixture(scope="session")
def server():
    return create_server(str(SKILLS_DIR))


def _call_tool(server, name: str, args: dict | None = None):
    async def _run():
        async with Client(server) as client:
            return await client.call_tool(name, args or {})

    return asyncio.run(_run())


def _list_tool_names(server) -> list[str]:
    async def _run():
        async with Client(server) as client:
            return [t.name for t in await client.list_tools()]

    return asyncio.run(_run())


def _list_prompt_names(server) -> list[str]:
    async def _run():
        async with Client(server) as client:
            return [p.name for p in await client.list_prompts()]

    return asyncio.run(_run())


def _list_resource_uris(server) -> list[str]:
    async def _run():
        async with Client(server) as client:
            return [str(r.uri) for r in await client.list_resources()]

    return asyncio.run(_run())


def _list_resource_template_uris(server) -> list[str]:
    async def _run():
        async with Client(server) as client:
            templates = await client.list_resource_templates()
            return [str(t.uri_template) for t in templates]

    return asyncio.run(_run())


@pytest.fixture
def call_tool(server):
    def _call(name: str, args: dict | None = None):
        return _call_tool(server, name, args)

    return _call


@pytest.fixture
def tool_names(server):
    return _list_tool_names(server)


@pytest.fixture
def prompt_names(server):
    return _list_prompt_names(server)


@pytest.fixture
def resource_uris(server):
    return _list_resource_uris(server)


@pytest.fixture
def resource_template_uris(server):
    return _list_resource_template_uris(server)
