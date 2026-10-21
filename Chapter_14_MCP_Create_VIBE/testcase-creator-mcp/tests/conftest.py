"""Shared fixtures and helpers for the TC MCP test suite."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest
from fastmcp import Client

from tc_mcp import config
from tc_mcp.repository import Repository
from tc_mcp.server import create_server


@pytest.fixture(scope="session")
def repo() -> Repository:
    overlay = Path(tempfile.mkdtemp()) / "tc_additions.csv"
    return Repository(config.DATA_PATH, str(overlay))


@pytest.fixture(scope="session")
def server():
    overlay = Path(tempfile.mkdtemp()) / "tc_additions.csv"
    return create_server(overlay_path=str(overlay), allow_write=False)


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


@pytest.fixture
def call_tool(server):
    def _call(name: str, args: dict | None = None):
        return _call_tool(server, name, args)

    return _call


@pytest.fixture
def tool_names(server):
    return _list_tool_names(server)


@pytest.fixture
def write_server(tmp_path: Path):
    overlay = tmp_path / "tc_additions.csv"
    return create_server(overlay_path=str(overlay), allow_write=True)


@pytest.fixture
def call_write_tool(write_server):
    def _call(name: str, args: dict | None = None):
        return _call_tool(write_server, name, args)

    return _call


@pytest.fixture
def write_tool_names(write_server):
    return _list_tool_names(write_server)
