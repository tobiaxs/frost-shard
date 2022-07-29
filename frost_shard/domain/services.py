import asyncio
import datetime
from dataclasses import asdict
from functools import lru_cache
from typing import Any, Generic, Iterable, Iterator, TypeAlias, TypeVar

from cryptography.fernet import Fernet
from fastapi import UploadFile
from structlog import get_logger

from frost_shard.auth import models as auth_models
from frost_shard.domain import models
from frost_shard.domain.filters import FileFilters, PaginationParams
from frost_shard.domain.repository import Repository, paginate
from frost_shard.domain.storage import FileStorage

logger = get_logger(__name__)

FileReadModelT = TypeVar("FileReadModelT", bound=models.FileReadModel)
DictItems: TypeAlias = list[tuple[str, Any]]


def non_empty_dict_factory(items: DictItems) -> dict:
    """Create a non-empty dictionary from a list of tuples.

    Args:
        items (DictItems): List of tuples with keys and values.

    Returns:
        dict: Non-empty dictionary.
    """
    return {key: value for key, value in items if value}


class CryptoService:
    """Simple service to encrypt and decrypt messages using 'cryptography'."""

    def __init__(self, secret: str) -> None:
        self.fernet = Fernet(secret)

    @lru_cache
    def encrypt(self, msg: bytes) -> bytes:
        """Encrypt the message using the secret key."""
        return self.fernet.encrypt(msg)

    @lru_cache
    def decrypt(self, msg: bytes) -> bytes:
        """Decrypt the message using the secret key."""
        return self.fernet.decrypt(msg)


class FileService(Generic[FileReadModelT]):
    """Orchestrator for the files domain.

    Contains the business logic around the file model operations.
    """

    def __init__(
        self,
        *,
        repository: Repository[FileReadModelT, models.FileEncryptedModel],
        storage: FileStorage,
        crypto_service: CryptoService,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.crypto = crypto_service

    async def bulk_create(
        self,
        user: auth_models.RequestUserModel,
        data: models.FileCreateModel,
        files: list[UploadFile],
    ) -> list[FileReadModelT]:
        """Bulk create several files."""
        logger.info("Bulk creating files", user=user, data=data)
        # TODO: Default factory seems not working
        date = data.date or datetime.date.today()
        folder = self.crypto.encrypt(
            f"{user.email}:{date}".encode(),
        ).decode()
        return list(
            await asyncio.gather(
                *(self.create(file, user, data, folder) for file in files),
            ),
        )

    async def create(
        self,
        file: UploadFile,
        user: auth_models.RequestUserModel,
        data: models.FileCreateModel,
        folder: str,
    ) -> FileReadModelT:
        """Create a new file."""
        logger.info("Creating a new file", user=user, data=data)

        encrypted_email = self.crypto.encrypt(user.email.encode())
        encrypted_data = models.FileEncryptedModel(
            email=encrypted_email,
            # TODO: Default factory seems not working
            date=data.date or datetime.date.today(),
        )
        created_file = await self.repository.create(encrypted_data)

        # Upload file to the storage
        extension = file.filename.split(".")[-1]
        filename = (
            self.crypto.encrypt(str(created_file.id).encode()).decode()
            + f".{extension}"
        )
        self.storage.upload(folder, filename, file.file)

        return created_file

    async def collect(
        self,
        user: auth_models.RequestUserModel,
        filters: FileFilters,
        pagination: PaginationParams,
    ) -> list[models.FileDecryptedModel]:
        """Collect, filter and paginate all the files for given parameters."""
        logger.info(
            "Fetching files",
            user=user,
            filters=filters,
            pagination=pagination,
        )

        # Prepare filters, remove email and default it to the user's email
        filters_dict = asdict(filters, dict_factory=non_empty_dict_factory)
        email = filters_dict.pop("email", user.email)

        # Fetch filtered files and prepare email filter generator
        files = await self.repository.collect(**filters_dict)
        files_per_email = (
            file
            for file in files
            if self.crypto.decrypt(file.email).decode() == email
        )

        # Paginate filtered files
        paginated_files = list(
            paginate(
                files_per_email,
                pagination.page,
                pagination.limit,
            ),
        )

        # Map repository and storage file to actual files
        storage_files = self.storage.collect()
        decrypted_files = self.map_repository_files_to_storage_files(
            paginated_files,
            storage_files,
        )
        return list(decrypted_files)

    def map_repository_files_to_storage_files(
        self,
        repository_files: Iterable[FileReadModelT],
        storage_files: Iterable[models.FileStorageModel],
    ) -> Iterator[models.FileDecryptedModel]:
        """Match the repository files with the ones in the file storage.

        Given a list of repository files and a list of storage files,
        return a list of matched entities (based on the id) as a decrypted
        models.
        """
        # TODO: Make it async
        count = 0
        file_ids = [str(file.id) for file in repository_files]

        for storage_file in storage_files:
            folder, file_key = storage_file.key.split("/")
            file_id = self.crypto.decrypt(
                file_key.split(".")[0].encode(),
            ).decode()
            if file_id in file_ids:
                # If decoded file id was found in the repository uuids,
                # fetch the url and yield it as a decrypted file
                folder_name = self.crypto.decrypt(folder.encode()).decode()
                date_str = folder_name.split(":")[-1]
                yield models.FileDecryptedModel(
                    id=file_id,
                    date=datetime.date.fromisoformat(date_str),
                    url=self.storage.get_file_url(storage_file.key),
                )
                count += 1
            if count == len(file_ids):
                # Stop when there are already enough files mapped
                break
