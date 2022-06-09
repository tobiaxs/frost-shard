from typing import Generic, TypeVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from frost_shard.domain.repositories import CreateModel

# TODO: Temporary workaround for SQLModel caching problems
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

SQLModelT = TypeVar("SQLModelT", bound=SQLModel)


class SQLRepository(Generic[SQLModelT, CreateModel]):
    """Concrete repository for the SQL database models."""

    session: AsyncSession

    def __init__(self, table: type[SQLModelT]) -> None:
        self.table = table

    async def create(self, data: CreateModel) -> SQLModelT:
        """Create a new object of the 'table' type."""
        entry = self.table.from_orm(data)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def collect(self) -> list[SQLModelT]:
        """Collect all objects of the 'table' type."""
        result = await self.session.execute(select(self.table))
        # TODO: For some reason every entry is a one element tuple
        return [entry[0] for entry in result.all()]
