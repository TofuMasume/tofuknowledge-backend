import pytest
import starlette.status

from api.settings import get_settings


@pytest.mark.asyncio
async def test_authorized_request_succeeds(async_client):
    response = await async_client.get("/articles")
    assert response.status_code == starlette.status.HTTP_200_OK


@pytest.mark.asyncio
async def test_missing_token_is_rejected(async_client):
    async_client.headers.pop("Authorization", None)
    response = await async_client.get("/articles")
    assert response.status_code == starlette.status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_invalid_token_is_rejected(async_client):
    async_client.headers["Authorization"] = "Bearer invalid"
    response = await async_client.get("/articles")
    assert response.status_code == starlette.status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_plain_token_format_is_accepted(async_client):
    settings = get_settings()
    async_client.headers["Authorization"] = settings.api_key
    response = await async_client.get("/articles")
    assert response.status_code == starlette.status.HTTP_200_OK
