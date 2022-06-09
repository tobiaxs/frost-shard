from typing import AsyncGenerator, Callable, TypeAlias

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from frost_shard.settings import settings

SessionGenerator: TypeAlias = AsyncGenerator[AsyncSession, None]


def get_session_factory(database_url: str) -> Callable[..., AsyncSession]:
    """Return a session factory for the given database URL."""
    return sessionmaker(
        bind=create_async_engine(database_url),
        class_=AsyncSession,  # type: ignore
        expire_on_commit=False,
    )


session_factory = get_session_factory(
    settings.DATABASE_URL + settings.DATABASE_NAME,
)


async def get_db_session() -> SessionGenerator:  # pragma: no cover
    """Return an async database session."""
    async with session_factory() as session:
        yield session
