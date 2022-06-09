from typing import TypeAlias

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from frost_shard.database.connection import get_db_session
from frost_shard.database.models import FileSQLModel
from frost_shard.database.repository import SQLRepository
from frost_shard.domain.models import FileCreateModel
from frost_shard.domain.services import FileService

FileSQLRepository: TypeAlias = SQLRepository[FileSQLModel, FileCreateModel]


def get_file_service(
    session: AsyncSession = Depends(get_db_session),
) -> FileService[FileSQLModel]:
    """Get the file service."""
    # TODO: This could be cached
    repository: FileSQLRepository = SQLRepository(FileSQLModel)
    repository.session = session
    return FileService(repository=repository)
