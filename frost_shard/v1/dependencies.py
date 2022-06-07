from functools import lru_cache

from frost_shard.database.models import FileSQLModel
from frost_shard.database.repository import SQLRepository
from frost_shard.domain.services import FileService


@lru_cache(maxsize=1)
def get_file_service() -> FileService[FileSQLModel]:
    """Get the file service.

    Cached with the database session inside the repository.
    """
    return FileService(SQLRepository(FileSQLModel))
