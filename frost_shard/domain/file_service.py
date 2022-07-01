from dataclasses import asdict
from typing import Any, Generic, TypeAlias, TypeVar

from structlog import get_logger

from frost_shard.auth import exceptions
from frost_shard.auth import models as auth_models
from frost_shard.domain import models
from frost_shard.domain.crypto_service import CryptoService
from frost_shard.domain.repository import Repository, paginate
from frost_shard.v1.filters import FileFilters, PaginationParams

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


class FileService(Generic[FileReadModelT]):
    """Orchestrator for the files domain.

    Contains the business logic around the file model operations.
    """

    def __init__(
        self,
        *,
        repository: Repository[FileReadModelT, models.FileEncryptedModel],
        crypto_service: CryptoService,
    ) -> None:
        self.repository = repository
        self.crypto = crypto_service

    async def create(
        self,
        user: auth_models.RequestUserModel,
        data: models.FileCreateModel,
    ) -> FileReadModelT:
        """Create a new file."""
        logger.info("Creating a new file", user=user, data=data)

        encrypted_email = self.crypto.encrypt(user.email.encode())
        encrypted_data = models.FileEncryptedModel(
            email=encrypted_email,
            date=data.date,
        )
        return await self.repository.create(encrypted_data)

    async def collect(
        self,
        user: auth_models.RequestUserModel,
        filters: FileFilters,
        pagination: PaginationParams,
    ) -> list[FileReadModelT]:
        """Collect, filter and paginate all the files for given parameters."""
        logger.info(
            "Fetching files",
            user=user,
            filters=filters,
            pagination=pagination,
        )

        # Prepare filters
        filters_dict = asdict(filters, dict_factory=non_empty_dict_factory)
        # Remove email from the filters and default it to the user's email
        email = filters_dict.pop("email", user.email)

        # Prevent non-admin users from filtering all the files
        if email != user.email and auth_models.UserRole.ADMIN not in user.roles:
            logger.error(
                "Non-admin user trying to filter not his files",
                user=user,
            )
            raise exceptions.PermissionsError

        # Fetch filtered files and prepare email filter generator
        files = await self.repository.collect(**filters_dict)
        files_per_email = (
            file
            for file in files
            if self.crypto.decrypt(file.email).decode() == email
        )

        # TODO: Move the pagination out of here or try to do it with redis
        # Paginate filtered files
        paginated_files = paginate(
            files_per_email,
            pagination.page,
            pagination.limit,
        )
        return list(paginated_files)
