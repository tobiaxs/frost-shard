from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from frost_shard.database import connection
from frost_shard.main import app as base_app
from frost_shard.settings import settings


@pytest_asyncio.fixture()
async def database_session() -> connection.SessionGenerator:
    """Prepare a test database session."""
    engine_factory = create_async_engine(settings.DATABASE_URL)
    session_factory = connection.get_session_factory(settings.DATABASE_URL)

    async with engine_factory.begin() as engine:
        # Clear all the data and migrate the tables.
        await engine.run_sync(SQLModel.metadata.drop_all)
        await engine.run_sync(SQLModel.metadata.create_all)

        async with session_factory(bind=engine) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def test_app(database_session: AsyncSession) -> FastAPI:
    """Create a test FastAPI application with overridden dependencies."""

    async def override_get_db() -> AsyncSession:
        return database_session

    base_app.dependency_overrides[connection.get_db_session] = override_get_db
    return base_app


@pytest_asyncio.fixture()
async def http_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an instance of the HTTP client."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
