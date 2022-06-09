from fastapi import APIRouter, Depends, status

from frost_shard.database.models import FileSQLModel
from frost_shard.domain.models import FileCreateModel
from frost_shard.domain.services import FileService
from frost_shard.v1.dependencies import get_file_service

router = APIRouter(tags=["v1"], prefix="/v1")


@router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    response_model=FileSQLModel,
)
async def create_file(
    body: FileCreateModel,
    service: FileService[FileSQLModel] = Depends(get_file_service),
) -> FileSQLModel:
    """Create a new file.

    Args:
        body (FileCreateModel): Data for the new file.

    Returns:
        FileSQLModel: Created file.
    """
    return await service.create(body)


@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    response_model=list[FileSQLModel],
)
async def get_files(
    service: FileService[FileSQLModel] = Depends(get_file_service),
) -> list[FileSQLModel]:
    """Fetch all files.

    Returns:
        list[FileSQLModel]: List of all files.
    """
    return await service.collect()
