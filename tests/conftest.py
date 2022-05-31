"""Tests fixtures."""

from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from frost_shard.main import app as base_app


@pytest_asyncio.fixture()
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an instance of the HTTP client."""
    async with AsyncClient(app=base_app, base_url="http://test") as client:
        yield client
