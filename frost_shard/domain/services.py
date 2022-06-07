from typing import Generic

from structlog import get_logger

from frost_shard.domain.models import FileCreateModel
from frost_shard.domain.repositories import ReadModel, Repository

logger = get_logger(__name__)


class FileService(Generic[ReadModel]):
    """Orchestrator for the files domain.

    Contains the business logic around the file model operations.
    """

    def __init__(
        self,
        repository: Repository[ReadModel, FileCreateModel],
    ) -> None:
        self.repository = repository

    def create(self, data: FileCreateModel) -> ReadModel:
        """Create a new file.

        Args:
            data (FileCreateModel): Data to create the file with.

        Returns:
            ReadModel: Created file.
        """
        logger.info("Creating a new file", data=data)
        file = self.repository.create(data)
        logger.info("A new file created", file=file)
        return file

    def collect(self) -> list[ReadModel]:
        """Collect all files.

        Returns:
            list[ReadModel]: List of all files.
        """
        return self.repository.collect()
