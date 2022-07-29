from functools import lru_cache
from typing import TypeAlias

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from frost_shard.database.sql.connection import get_db_session
from frost_shard.database.sql.models import FileSQLModel
from frost_shard.database.sql.repository import SQLRepository
from frost_shard.domain.models import FileEncryptedModel
from frost_shard.domain.services import CryptoService, FileService
from frost_shard.settings import settings
from frost_shard.storage.aws import S3Storage

FileSQLRepository: TypeAlias = SQLRepository[FileSQLModel, FileEncryptedModel]


@lru_cache
def _get_file_service() -> FileService:
    """Initialize the file service with it's dependencies."""
    repository: FileSQLRepository = SQLRepository(FileSQLModel)
    storage = S3Storage()
    return FileService(
        repository=repository,
        storage=storage,
        crypto_service=CryptoService(settings.SECRET_KEY),
    )


def get_file_service(
    session: AsyncSession = Depends(get_db_session),
) -> FileService:
    """Get the file service."""
    srv = _get_file_service()
    # TODO: Check how the session is not dying
    setattr(srv.repository, "session", session)
    return srv
