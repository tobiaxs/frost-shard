from typing import Generic, Iterable, Iterator, Protocol, TypeVar

from pydantic import BaseModel

ReadModel = TypeVar("ReadModel")
CreateModel = TypeVar("CreateModel", bound=BaseModel, contravariant=True)
PaginationEntry = TypeVar("PaginationEntry")


def paginate(
    entries: Iterable[PaginationEntry],
    page: int,
    limit: int,
) -> Iterator[PaginationEntry]:
    """Paginate a list of entries.

    Args:
        entries (Iterable[PaginationEntry]): Iterable of entries.
        page (int): Page number.
        limit (int): Number of entries per page.

    Yields:
        Iterator[PaginationEntry]: Paginated entries.
    """
    offset = page * limit
    end = offset + limit - 1
    for index, entry in enumerate(entries):
        if index >= offset:
            yield entry
        if index == end:
            break


class Repository(Protocol, Generic[ReadModel, CreateModel]):
    """Abstraction over the idea of persistent storage.

    Interface class for all the concrete repository implementations.
    """

    async def create(self, data: CreateModel) -> ReadModel:
        """Create a new entry with given data."""
        ...

    async def collect(self, **filters) -> list[ReadModel]:
        """Collect all entries matching the given filters."""
        ...
