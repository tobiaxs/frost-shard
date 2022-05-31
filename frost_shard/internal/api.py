from fastapi import APIRouter, status

router = APIRouter(tags=["internal"], include_in_schema=False)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {"example": {"detail": "Ok"}}},
        },
    },
)
async def healthcheck() -> dict:
    """Health check endpoint.

    Returns:
        dict: Status of the service.
    """
    return {"detail": "Ok"}
