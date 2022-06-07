from typing import Generic, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from frost_shard.database.connection import get_db_session
from frost_shard.domain.repositories import CreateModel

# TODO: Temporary workaround for SQLModel caching problems
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

SQLModelT = TypeVar("SQLModelT", bound=SQLModel)


class SQLRepository(Generic[SQLModelT, CreateModel]):
    """Concrete repository for the SQL database models."""

    def __init__(self, table: type[SQLModelT]) -> None:
        self.table = table
        self.session = next(get_db_session())

    def create(self, data: CreateModel) -> SQLModelT:
        """Create a new object of the 'table' type."""
        obj = self.table.from_orm(data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def collect(self) -> list[SQLModelT]:
        """Collect all objects of the 'table' type."""
        query = select(self.table)
        return self.session.exec(query).all()
