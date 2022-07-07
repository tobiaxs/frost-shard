from fastapi import Depends
from structlog import get_logger

from frost_shard.auth import dependencies, enums, exceptions, models
from frost_shard.domain.filters import FileFilters

logger = get_logger(__name__)


def validate_filters(
    user: models.RequestUserModel = Depends(dependencies.get_request_user),
    file_filters: FileFilters = Depends(),
) -> None:
    """Prevent not permitted users from filtering all the files."""
    if file_filters.email == user.email:
        return
    if enums.UserPermission.READ_GLOBAL_FILES in user.permissions:
        return

    logger.error(
        "User trying to filter not his files",
        user=user,
    )
    raise exceptions.PermissionsError()
