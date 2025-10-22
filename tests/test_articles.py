import pytest
import starlette.status


@pytest.mark.asyncio
async def test_article_crud_flow(async_client):
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "記事著者",
            "email": "author@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    # 記事作成
    create_response = await async_client.post(
        "/articles",
        json={
            "title": "テスト記事",
            "summary": "テストサマリー",
            "author_id": user_id,
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
            "author_id": user_id,
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
async def test_article_update_fails_when_author_missing(async_client):
    # 著者作成
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "記事著者",
            "email": "author@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    # 記事作成
    create_response = await async_client.post(
        "/articles",
        json={
            "title": "テスト記事",
            "summary": "テストサマリー",
            "author_id": user_id,
        },
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    article_id = create_response.json()["article_id"]

    # 存在しない著者IDで更新
    update_response = await async_client.put(
        f"/articles/{article_id}",
        json={
            "article_id": article_id,
            "author_id": user_id + 1,
            "title": "更新失敗タイトル",
            "summary": "更新失敗サマリー",
        },
    )
    assert update_response.status_code == starlette.status.HTTP_404_NOT_FOUND
    assert (
        update_response.json()["detail"]
        == "著者となるユーザーが見つかりません。"
    )


@pytest.mark.asyncio
async def test_article_tag_crud_flow(async_client):
    # ユーザーと記事を作成
    user_response = await async_client.post(
        "/users",
        json={
            "user_name": "タグ著者",
            "email": "tag-author@example.com",
        },
    )
    assert user_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = user_response.json()["user_id"]

    article_response = await async_client.post(
        "/articles",
        json={
            "title": "タグ付き記事",
            "summary": "タグテスト用",
            "author_id": user_id,
        },
    )
    assert article_response.status_code == starlette.status.HTTP_201_CREATED
    article_id = article_response.json()["article_id"]

    # タグを2つ作成
    tag_python = await async_client.post(
        "/tags",
        json={"tag_name": "Python"},
    )
    assert tag_python.status_code == starlette.status.HTTP_201_CREATED
    python_id = tag_python.json()["tag_id"]

    tag_fastapi = await async_client.post(
        "/tags",
        json={"tag_name": "FastAPI"},
    )
    assert tag_fastapi.status_code == starlette.status.HTTP_201_CREATED
    fastapi_id = tag_fastapi.json()["tag_id"]

    # 初期状態はタグなし
    list_response = await async_client.get(f"/articles/{article_id}/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == []

    # タグ1を追加
    add_python = await async_client.post(
        f"/articles/{article_id}/tags/{python_id}"
    )
    assert add_python.status_code == starlette.status.HTTP_201_CREATED
    assert add_python.json() == {
        "tag_id": python_id,
        "tag_name": "Python",
    }

    # 既に紐づいている場合は409
    duplicate_python = await async_client.post(
        f"/articles/{article_id}/tags/{python_id}"
    )
    assert duplicate_python.status_code == starlette.status.HTTP_409_CONFLICT
    assert (
        duplicate_python.json()["detail"]
        == "タグは既に記事に紐づいています。"
    )

    # タグ2を追加
    add_fastapi = await async_client.post(
        f"/articles/{article_id}/tags/{fastapi_id}"
    )
    assert add_fastapi.status_code == starlette.status.HTTP_201_CREATED
    assert add_fastapi.json()["tag_name"] == "FastAPI"

    # 記事に紐づくタグを取得
    list_response = await async_client.get(f"/articles/{article_id}/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    tags = list_response.json()
    assert tags == [
        {"tag_id": python_id, "tag_name": "Python"},
        {"tag_id": fastapi_id, "tag_name": "FastAPI"},
    ]

    # 関連除去
    delete_python = await async_client.delete(
        f"/articles/{article_id}/tags/{python_id}"
    )
    assert delete_python.status_code == starlette.status.HTTP_204_NO_CONTENT

    # 再削除は404
    delete_python_again = await async_client.delete(
        f"/articles/{article_id}/tags/{python_id}"
    )
    assert delete_python_again.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        delete_python_again.json()["detail"]
        == "記事とタグの紐づけが見つかりません。"
    )

    # タグが1つだけ残っている
    list_response = await async_client.get(f"/articles/{article_id}/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == [
        {"tag_id": fastapi_id, "tag_name": "FastAPI"}
    ]

    # 存在しない記事/タグでの追加は404
    missing_article = await async_client.post(
        f"/articles/{article_id + 999}/tags/{fastapi_id}"
    )
    assert missing_article.status_code == starlette.status.HTTP_404_NOT_FOUND
    assert missing_article.json()["detail"] == "記事が見つかりません。"

    missing_tag = await async_client.post(
        f"/articles/{article_id}/tags/{fastapi_id + 999}"
    )
    assert missing_tag.status_code == starlette.status.HTTP_404_NOT_FOUND
    assert missing_tag.json()["detail"] == "タグが見つかりません。"
