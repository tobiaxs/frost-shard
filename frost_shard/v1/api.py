from fastapi import APIRouter, Depends, File, UploadFile, status

from frost_shard.auth.dependencies import get_request_user, has_permissions
from frost_shard.auth.enums import UserPermission
from frost_shard.auth.models import RequestUserModel
from frost_shard.database.sql.models import FileSQLModel
from frost_shard.domain.filters import FileFilters, PaginationParams
from frost_shard.domain.models import FileCreateModel, FileDecryptedModel
from frost_shard.domain.permissions import validate_filters
from frost_shard.domain.services import FileService
from frost_shard.v1.dependencies import get_file_service

router = APIRouter(tags=["v1"], prefix="/api/v1")


@router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    response_model=list[FileSQLModel],
    dependencies=(Depends(has_permissions((UserPermission.CREATE_FILES,))),),
)
async def create_files(
    # FastAPI is getting angry without Depends
    body: FileCreateModel = Depends(),
    files: list[UploadFile] = File(...),
    user: RequestUserModel = Depends(get_request_user),
    file_service: FileService[FileSQLModel] = Depends(get_file_service),
) -> list[FileSQLModel]:
    """Create a new files.

    Args:
        body (FileCreateModel): Data for the new files.
        files (list[UploadFile]): Files to upload.
        user (RequestUserModel): Request User.
        file_service (FileService): File service.

    Returns:
        tuple[FileSQLModel]: Created files.
    """
    return await file_service.bulk_create(user, body, files)


@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    response_model=list[FileDecryptedModel],
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
) -> list[FileDecryptedModel]:
    """Get all files based on provided filters.

    Args:
        file_service (FileService): File service.
        file_filters (FileFilters): File filters.
        pagination (PaginationParams): Pagination parameters.

    Returns:
        list[FileDecryptedModel]: List of files.
    """
    return await file_service.collect(user, file_filters, pagination)
