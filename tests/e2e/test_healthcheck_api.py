import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = [pytest.mark.asyncio]


async def test_healthcheck_endpoint(http_client: AsyncClient):
    """Check that health check endpoint is returning a proper response."""
    response = await http_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Ok"
