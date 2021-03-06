from fastapi import APIRouter, Depends, status

from frost_shard.auth.dependencies import get_request_user, has_permissions
from frost_shard.auth.enums import UserPermission
from frost_shard.auth.models import RequestUserModel
from frost_shard.database.models import FileSQLModel
from frost_shard.domain.file_service import FileService
from frost_shard.domain.filters import FileFilters, PaginationParams
from frost_shard.domain.models import FileCreateModel
from frost_shard.domain.permissions import validate_filters
from frost_shard.v1.dependencies import get_file_service

router = APIRouter(tags=["v1"], prefix="/api/v1")


@router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    response_model=FileSQLModel,
    dependencies=(Depends(has_permissions((UserPermission.CREATE_FILES,))),),
)
async def create_file(
    body: FileCreateModel,
    user: RequestUserModel = Depends(get_request_user),
    file_service: FileService[FileSQLModel] = Depends(get_file_service),
) -> FileSQLModel:
    """Create a new file.

    Args:
        body (FileCreateModel): Data for the new file.
        file_service (FileService): File service.

    Returns:
        FileSQLModel: Created file.
    """
    return await file_service.create(user, body)


@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    response_model=list[FileSQLModel],
    dependencies=(
        Depends(has_permissions((UserPermission.READ_FILES,))),
        Depends(validate_filters),
    ),
)
async def get_files(
    user: RequestUserModel = Depends(get_request_user),
    file_service: FileService[FileSQLModel] = Depends(get_file_service),
    file_filters: FileFilters = Depends(),
    pagination: PaginationParams = Depends(),
) -> list[FileSQLModel]:
    """Get all files based on provided filters.

    Args:
        file_service (FileService): File service.
        file_filters (FileFilters): File filters.
        pagination (PaginationParams): Pagination parameters.

    Returns:
        list[FileSQLModel]: List of files.
    """
    return await file_service.collect(user, file_filters, pagination)
