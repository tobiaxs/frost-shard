from fastapi import APIRouter, responses, status

from frost_shard.settings import settings

router = APIRouter(tags=["internal"], include_in_schema=False)


@router.get("/")
async def redirect_to_docs() -> responses.RedirectResponse:
    """Redirect root requests to the docs.

    Returns:
        RedirectResponse: Redirect to the docs page.
    """
    return responses.RedirectResponse(f"{settings.API_PREFIX}/api/docs")


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
