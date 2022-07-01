import datetime
from typing import Callable

import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import EmailStr

from frost_shard.auth.models import RequestUserModel, UserRole
from frost_shard.domain.crypto_service import CryptoService
from frost_shard.settings import settings
from tests.conftest import TEST_USER_EMAIL

pytestmark = pytest.mark.asyncio

FILES_ROUTE = "/api/v1/files"


async def test_files_create_api(http_client: AsyncClient) -> None:
    """Check that create endpoint is responding with created file."""
    response = await http_client.post(FILES_ROUTE, json={})
    data = response.json()
    crypto = CryptoService(settings.SECRET_KEY)

    assert response.status_code == status.HTTP_201_CREATED
    assert data["id"] is not None
    assert crypto.decrypt(data["email"].encode()).decode() == TEST_USER_EMAIL
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
    for number in range(1, 6):
        await http_client.post(
            FILES_ROUTE,
            json={"date": f"2020-01-0{number}"},
        )

    response = await http_client.get("/api/v1/files")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 5


async def test_files_list_api_with_email_filter(
    http_client: AsyncClient,
    get_http_client: Callable[..., AsyncClient],
) -> None:
    """Check that list endpoint is responding with list of files filtered by email."""
    # Create 2 files using API
    for number in range(2):
        client = get_http_client(
            user=RequestUserModel(
                email=EmailStr(f"test{number}@email.com"),
                roles=[UserRole.ADMIN],
            )
        )
        await client.post(FILES_ROUTE, json={})

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
            json={"date": f"2020-01-0{number}"},
        )

    response = await http_client.get(
        f"{FILES_ROUTE}?email={TEST_USER_EMAIL}&date__gt=2020-01-02&date__lt=2020-01-05"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2


async def test_files_list_api_with_non_admin_filter(
    get_http_client: Callable[..., AsyncClient],
) -> None:
    """Check that filtering with different email with non-admin users returns 403."""
    regular_client = get_http_client(
        user=RequestUserModel(
            email=EmailStr(f"test-regular@email.com"),
            roles=[UserRole.REGULAR],
        )
    )
    response = await regular_client.get(
        f"{FILES_ROUTE}?email=test-admin@email.com"
    )
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["detail"] == "User is not allowed to perform this action"
