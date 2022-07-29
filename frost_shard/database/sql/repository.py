from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from frost_shard.database.sql.expressions import create_expressions

# TODO: Temporary workaround for SQLModel caching problems
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

ReadModel = TypeVar("ReadModel", bound=SQLModel)
CreateModel = TypeVar("CreateModel", bound=BaseModel)


class SQLRepository(Generic[ReadModel, CreateModel]):
    """Concrete repository for the SQL database models."""

    session: AsyncSession

    def __init__(self, table: type[ReadModel]) -> None:
        self.table = table

    async def create(self, data: CreateModel) -> ReadModel:
        """Create a new entry of the 'table' type.

        Object will not be committed to the database
        until the session is closed.
        """
        entry = self.table.from_orm(data)
        self.session.add(entry)
        return entry

    async def collect(self, **filters: dict[str, Any]) -> list[ReadModel]:
        """Collect all objects of the 'table' type matching given filters."""
        query = select(self.table)
        if filters:
            expressions = create_expressions(self.table, filters)
            query = select(self.table).where(*expressions)
        result = await self.session.execute(query)
        # For some reason every entry is a one element tuple
        return [entry[0] for entry in result.all()]
