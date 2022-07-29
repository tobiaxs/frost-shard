import datetime
import uuid
from typing import Protocol

from pydantic import BaseModel, Field


class FileReadModel(Protocol):
    """Structural model for the file response."""

    id: uuid.UUID
    email: bytes
    date: datetime.date | None


class FileCreateModel(BaseModel):
    """Data model for the incoming file payload."""

    date: datetime.date | None = Field(default_factory=datetime.date.today)

    class Config:
        frozen = True


class FileEncryptedModel(BaseModel):
    """Data model for the file creation."""

    email: bytes
    date: datetime.date | None = Field(default_factory=datetime.date.today)

    class Config:
        frozen = True


class FileStorageModel(BaseModel):
    """File from the storage."""

    key: str


class FileDecryptedModel(BaseModel):
    """File after decryption."""

    id: str
    date: datetime.date
    url: str

    class Config:
        frozen = True
