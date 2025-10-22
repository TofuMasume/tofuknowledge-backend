import pytest
import starlette.status

from api.settings import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_article_file_upload_and_download(async_client):
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "ファイル著者",
            "email": "file-author@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    # アップロード対象記事を作成
    create_response = await async_client.post(
        "/articles",
        json={
            "title": "ファイル記事",
            "summary": None,
            "author_id": user_id,
        },
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
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
    storage_dir = settings.article_storage_dir
    stored_file = storage_dir / upload_obj["filename"]
    if stored_file.exists():
        stored_file.unlink()
    if storage_dir.exists() and not any(storage_dir.iterdir()):
        storage_dir.rmdir()

    # 記事削除
    delete_response = await async_client.delete(f"/articles/{article_id}")
    assert delete_response.status_code == starlette.status.HTTP_200_OK


@pytest.mark.asyncio
async def test_article_file_upload_missing_article(async_client):
    files = {
        "file": ("missing.md", b"not found", "text/markdown"),
    }
    upload_response = await async_client.post(
        "/articles/999/file", files=files
    )
    assert upload_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        upload_response.json()["detail"] == "記事が見つかりません。"
    )


@pytest.mark.asyncio
async def test_article_file_upload_requires_filename(async_client):
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "ファイル名なし著者",
            "email": "no-filename@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    article_response = await async_client.post(
        "/articles",
        json={
            "title": "ファイル名なし記事",
            "summary": "ファイル名未指定の検証",
            "author_id": user_id,
        },
    )
    assert article_response.status_code == starlette.status.HTTP_201_CREATED
    article_id = article_response.json()["article_id"]

    files = {
        "file": ("", b"no filename", "text/plain"),
    }
    upload_response = await async_client.post(
        f"/articles/{article_id}/file", files=files
    )
    # FastAPIのバリデーションで弾かれるため422になる
    assert upload_response.status_code == (
        starlette.status.HTTP_422_UNPROCESSABLE_CONTENT
    )
    detail = upload_response.json()["detail"][0]
    assert "UploadFile" in detail["msg"]


@pytest.mark.asyncio
async def test_article_file_download_without_upload(async_client):
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "未アップロード著者",
            "email": "no-upload@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    article_response = await async_client.post(
        "/articles",
        json={
            "title": "ファイル未登録記事",
            "summary": None,
            "author_id": user_id,
        },
    )
    assert article_response.status_code == starlette.status.HTTP_201_CREATED
    article_id = article_response.json()["article_id"]

    download_response = await async_client.get(
        f"/articles/{article_id}/file"
    )
    assert download_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        download_response.json()["detail"]
        == "記事ファイルが見つかりません。"
    )
