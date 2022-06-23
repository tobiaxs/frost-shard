import datetime
import uuid
from typing import Protocol

from pydantic import BaseModel, EmailStr


class FileReadModel(Protocol):
    """Structural model for the file response."""

    id: uuid.UUID | None
    email: bytes
    date: datetime.date | None


class FileCreateModel(BaseModel):
    """Data model for the incoming file payload."""

    email: EmailStr
    date: datetime.date | None = None

    class Config:
        frozen = True


class FileEncryptedModel(BaseModel):
    """Data model for the file creation."""

    email: bytes
    date: datetime.date | None = None

    class Config:
        frozen = True
