import datetime
import uuid
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    """Base class for all SQL models."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    def __init_subclass__(cls, *args, **kwargs) -> None:
        """Satisfy mypy type checking."""

    @declared_attr
    def __tablename__(self) -> str:
        """Return the table name."""
        return self.__name__.lower()


class FileSQLModel(BaseSQLModel, table=True):
    """SQL model for the file table."""

    __name__ = "files"
    email: EmailStr
    date: Optional[datetime.date] = Field(default_factory=datetime.date.today)
