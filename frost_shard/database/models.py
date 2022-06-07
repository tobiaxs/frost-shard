import datetime
import uuid
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    """Base class for all SQL models."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    def __init_subclass__(cls, *args, **kwargs) -> None:
        """Satisfy mypy type checking."""


class FileSQLModel(BaseSQLModel, table=True):
    """SQL model for the file table."""

    email: EmailStr
    date: Optional[datetime.date] = Field(default_factory=datetime.date.today)
