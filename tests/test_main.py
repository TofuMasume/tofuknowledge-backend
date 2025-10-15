from pathlib import Path

import pytest
import pytest_asyncio
import starlette.status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import api.models.articles  # noqa: F401  # モデルをmetadataに登録
import api.models.users  # noqa: F401
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
async def test_article_crud_flow(async_client):
    # 記事作成
    create_response = await async_client.post(
        "/articles",
        json={
            "title": "テスト記事",
            "summary": "テストサマリー",
            "author_id": 1,
        },
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    created = create_response.json()
    assert created["title"] == "テスト記事"
    assert created["summary"] == "テストサマリー"
    article_id = created["article_id"]

    # 記事一覧
    list_response = await async_client.get("/articles")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    articles = list_response.json()
    assert len(articles) == 1
    assert articles[0]["title"] == "テスト記事"

    # 記事詳細
    detail_response = await async_client.get(f"/articles/{article_id}")
    assert detail_response.status_code == starlette.status.HTTP_200_OK
    detail = detail_response.json()
    assert detail["summary"] == "テストサマリー"

    # 記事更新
    update_response = await async_client.put(
        f"/articles/{article_id}",
        json={
            "article_id": article_id,
            "author_id": 1,
            "title": "更新後タイトル",
            "summary": "更新後サマリー",
        },
    )
    assert update_response.status_code == starlette.status.HTTP_200_OK
    updated = update_response.json()
    assert updated["title"] == "更新後タイトル"
    assert updated["summary"] == "更新後サマリー"

    # 更新後の詳細確認
    detail_response = await async_client.get(f"/articles/{article_id}")
    assert detail_response.status_code == starlette.status.HTTP_200_OK
    detail = detail_response.json()
    assert detail["title"] == "更新後タイトル"
    assert detail["summary"] == "更新後サマリー"

    # 記事削除
    delete_response = await async_client.delete(f"/articles/{article_id}")
    assert delete_response.status_code == starlette.status.HTTP_200_OK
    deleted = delete_response.json()
    assert deleted["article_id"] == article_id

    # 削除後の一覧は空
    list_response = await async_client.get("/articles")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == []

    # 削除済み記事は取得できない
    detail_response = await async_client.get(f"/articles/{article_id}")
    assert detail_response.status_code == starlette.status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_article_file_upload_and_download(async_client):
    # アップロード対象記事を作成
    create_response = await async_client.post(
        "/articles",
        json={
            "title": "ファイル記事",
            "summary": None,
            "author_id": 1,
        },
    )
    article_id = create_response.json()["article_id"]

    # ファイルアップロード
    upload_bytes = b"# test article"
    files = {
        "file": ("sample.md", upload_bytes, "text/markdown"),
    }
    upload_response = await async_client.post(
        f"/articles/{article_id}/file", files=files
    )
    assert upload_response.status_code == starlette.status.HTTP_201_CREATED
    upload_obj = upload_response.json()
    assert upload_obj["article_id"] == article_id
    assert upload_obj["filename"].endswith(".md")

    # ファイルダウンロード
    download_response = await async_client.get(
        f"/articles/{article_id}/file"
    )
    assert download_response.status_code == starlette.status.HTTP_200_OK
    assert download_response.content == upload_bytes
    content_disposition = download_response.headers["content-disposition"]
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

    # 記事削除
    delete_response = await async_client.delete(f"/articles/{article_id}")
    assert delete_response.status_code == starlette.status.HTTP_200_OK
