from typing import TypeAlias

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from frost_shard.database.connection import get_db_session
from frost_shard.database.models import FileSQLModel
from frost_shard.database.sql_repository import SQLRepository
from frost_shard.domain.file_service import FileService
from frost_shard.domain.models import FileEncryptedModel

FileSQLRepository: TypeAlias = SQLRepository[FileSQLModel, FileEncryptedModel]


def get_file_service(
    session: AsyncSession = Depends(get_db_session),
) -> FileService:
    """Initialize the file service with it's dependencies."""
    # TODO: Cache the session
    repository: FileSQLRepository = SQLRepository(FileSQLModel)
    repository.session = session
    return FileService(repository=repository)
