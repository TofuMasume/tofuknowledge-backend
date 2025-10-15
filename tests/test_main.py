from pathlib import Path

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
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client


# test


@pytest.mark.asyncio
async def test_article_create_and_read(async_client):
    # 記事作成
    response = await async_client.post(
        "/articles",
        json={
            "title": "テスト記事",
            "summary": "テストサマリー",
            "author_id": 1,
        },
    )
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テスト記事"
    article_id = response_obj["article_id"]
    # 記事詳細取得
    response = await async_client.get(f"/articles/{article_id}")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["article_id"] == article_id
    assert response_obj["title"].startswith("article")


@pytest.mark.asyncio
async def test_article_file_upload_and_download(async_client):
    # ファイルアップロード
    upload_bytes = b"# test article"
    files = {
        "file": ("sample.md", upload_bytes, "text/markdown"),
    }
    response = await async_client.post("/articles/101/file", files=files)
    assert response.status_code == starlette.status.HTTP_201_CREATED
    upload_obj = response.json()
    assert upload_obj["article_id"] == 101
    assert upload_obj["filename"].endswith(".md")

    # ファイルダウンロード
    response = await async_client.get("/articles/101/file")
    assert response.status_code == starlette.status.HTTP_200_OK
    assert response.content == upload_bytes
    content_disposition = response.headers["content-disposition"]
    assert (
        f'filename="{upload_obj["filename"]}"' in content_disposition
    )

    # 片付け
    storage_dir = Path(__file__).resolve().parents[1] / "storage" / "articles"
    stored_file = storage_dir / upload_obj["filename"]
    if stored_file.exists():
        stored_file.unlink()
    if storage_dir.exists() and not any(storage_dir.iterdir()):
        storage_dir.rmdir()
