import pytest
import pytest_asyncio
import starlette.status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.db.db import Base, get_db
from api.main import app

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


# make client
@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    # make engine and session for Async
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
    )

    # init sqlite table on memory
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # override DB path by DI
    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    # return HTTP Async client for test
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# test


@pytest.mark.asyncio
async def test_article_create_and_read(async_client):
    # 記事作成
    response = await async_client.post(
        "/articles",
        json={
            "title": "テスト記事",
            "summery": "テストサマリー",
            "author_id": "テスト著者",
        },
    )
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テスト記事"
    article_id = response_obj["article_id"]
    # 記事取得
    response = await async_client.get("/articles")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "テスト記事"
    assert response_obj[0]["article_id"] == article_id
