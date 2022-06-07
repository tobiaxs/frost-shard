from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from frost_shard.settings import settings

database_url = settings.DATABASE_URL + settings.DATABASE_NAME
engine = create_engine(database_url)


def create_db_tables() -> None:
    """Migrate all the database tables."""
    SQLModel.metadata.create_all(engine)


def get_db_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session
