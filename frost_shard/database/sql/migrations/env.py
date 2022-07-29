import asyncio
from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncEngine  # type: ignore

from frost_shard.database.sql.models import *
from frost_shard.settings import settings

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = SQLModel.metadata


database_url = settings.DATABASE_URL + settings.DATABASE_NAME


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = AsyncEngine(
        create_engine(
            database_url,
            echo=True,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
