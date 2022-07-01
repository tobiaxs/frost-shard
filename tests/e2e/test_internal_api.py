import pytest
from fastapi import status
from httpx import AsyncClient

from frost_shard.settings import settings

pytestmark = [pytest.mark.asyncio]


async def test_root_endpoint(http_client: AsyncClient) -> None:
    """Check that root endpoint is redirecting to the docs page."""
    response = await http_client.get("/")

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.next_request is not None
    assert (
        response.next_request.url
        == f"http://test{settings.API_PREFIX}/api/docs"
    )


async def test_healthcheck_endpoint(http_client: AsyncClient) -> None:
    """Check that health check endpoint is returning a proper response."""
    response = await http_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Ok"
