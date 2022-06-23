import datetime

import pytest
from fastapi import status
from httpx import AsyncClient

from frost_shard.domain.crypto_service import CryptoService
from frost_shard.settings import settings

pytestmark = pytest.mark.asyncio

FILES_ROUTE = "/api/v1/files"
TEST_EMAIL = "test@email.com"


async def test_files_create_api(http_client: AsyncClient) -> None:
    """Check that create endpoint is responding with created file."""
    response = await http_client.post(
        FILES_ROUTE,
        json={"email": TEST_EMAIL},
    )
    data = response.json()
    crypto = CryptoService(settings.SECRET_KEY)

    assert response.status_code == status.HTTP_201_CREATED
    assert data["id"] is not None
    assert crypto.decrypt(data["email"].encode()).decode() == TEST_EMAIL
    assert data["date"] == str(datetime.date.today())


async def test_empty_files_list_api(http_client: AsyncClient) -> None:
    """Check that list endpoint is responding with empty list of files."""
    response = await http_client.get(f"{FILES_ROUTE}?email=test@email.com")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0


async def test_files_list_api(http_client: AsyncClient) -> None:
    """Check that list endpoint is responding with list of files."""
    # Create 5 files using API
    for _ in range(5):
        await http_client.post(
            FILES_ROUTE,
            json={"email": TEST_EMAIL},
        )

    response = await http_client.get("/api/v1/files?email=test@email.com")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 5


async def test_files_list_api_with_email_filter(
    http_client: AsyncClient,
) -> None:
    """Check that list endpoint is responding with list of files filtered by email."""
    # Create 2 files using API
    for number in range(2):
        await http_client.post(
            FILES_ROUTE,
            json={"email": f"test{number}@email.com"},
        )

    response = await http_client.get(f"{FILES_ROUTE}?email=test1@email.com")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1


async def test_files_list_api_with_date_filters(
    http_client: AsyncClient,
) -> None:
    """Check that list endpoint is responding with list of files filtered by date."""
    # Create 5 files with different dates using API
    for number in range(1, 6):
        await http_client.post(
            FILES_ROUTE,
            json={"email": "test1@email.com", "date": f"2020-01-0{number}"},
        )

    response = await http_client.get(
        f"{FILES_ROUTE}?email=test1@email.com&date__gt=2020-01-02&date__lt=2020-01-05"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2
