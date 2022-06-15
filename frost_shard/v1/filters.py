import datetime
from dataclasses import dataclass

from fastapi import Query
from pydantic import EmailStr


@dataclass(frozen=True)
class PaginationParams:
    """Pagination parameters."""

    page: int = Query(0)
    limit: int = Query(10)


@dataclass(frozen=True)
class FileFilters:
    """File API filters."""

    email: EmailStr = Query()  # TODO: Make it optional
    date__gt: datetime.date | None = Query(
        None,
        description="Date greater than",
        example=datetime.date(2020, 1, 1),
    )
    date__lt: datetime.date | None = Query(
        None,
        description="Date less than",
        example=datetime.date(2020, 1, 31),
    )
