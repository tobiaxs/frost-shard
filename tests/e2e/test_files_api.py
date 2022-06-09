import datetime

import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_files_create_api(http_client: AsyncClient) -> None:
    """Check that create endpoint is responding with created file."""
    response = await http_client.post(
        "/api/v1/files",
        json={"email": "test@email.com"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["id"] is not None
    assert data["email"] == "test@email.com"
    assert data["date"] == str(datetime.date.today())


async def test_files_list_api(http_client: AsyncClient) -> None:
    """Check that list endpoint is responding with list of files."""
    response = await http_client.get("/api/v1/files")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0
