from typing import BinaryIO, Protocol

from frost_shard.domain.models import FileStorageModel


class FileStorage(Protocol):
    """Abstraction over file storing service."""

    def upload(self, folder: str, filename: str, file: BinaryIO) -> None:
        """Upload a file to the storage."""
        ...

    def collect(self) -> list[FileStorageModel]:
        """Collect all files from the storage."""
        ...

    def get_file_url(self, key: str) -> str:
        """Get a download URL for a file."""
        ...
