import pytest
import starlette.status


@pytest.mark.asyncio
async def test_user_crud_flow(async_client):
    # ユーザー作成
    create_response = await async_client.post(
        "/users",
        json={
            "user_name": "Tofu Masume",
            "email": "tofu@example.com",
        },
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    created_user = create_response.json()
    user_id = created_user["user_id"]

    # ユーザー一覧
    list_response = await async_client.get("/users")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    users = list_response.json()
    assert len(users) == 1
    assert users[0]["user_name"] == "Tofu Masume"

    # ユーザー詳細
    detail_response = await async_client.get(f"/users/{user_id}")
    assert detail_response.status_code == starlette.status.HTTP_200_OK
    detail = detail_response.json()
    assert detail["email"] == "tofu@example.com"

    # ユーザー更新
    update_response = await async_client.put(
        f"/users/{user_id}",
        json={
            "user_name": "Updated Masume",
            "email": "updated@example.com",
        },
    )
    assert update_response.status_code == starlette.status.HTTP_200_OK
    updated = update_response.json()
    assert updated["user_name"] == "Updated Masume"
    assert updated["email"] == "updated@example.com"

    # ユーザー記事作成
    article_response = await async_client.post(
        "/articles",
        json={
            "title": "ユーザー記事",
            "summary": "ユーザーに紐づく記事",
            "author_id": user_id,
        },
    )
    assert article_response.status_code == starlette.status.HTTP_201_CREATED

    # ユーザー記事一覧
    user_articles_response = await async_client.get(
        f"/users/{user_id}/articles"
    )
    assert user_articles_response.status_code == starlette.status.HTTP_200_OK
    user_articles = user_articles_response.json()
    assert len(user_articles) == 1
    assert user_articles[0]["title"] == "ユーザー記事"
    assert user_articles[0]["author_id"] == user_id

    # ユーザー削除
    delete_response = await async_client.delete(f"/users/{user_id}")
    assert delete_response.status_code == starlette.status.HTTP_200_OK

    # 削除後は一覧に表示されない
    list_response = await async_client.get("/users")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == []

    # 削除後の詳細・記事は404
    detail_response = await async_client.get(f"/users/{user_id}")
    assert detail_response.status_code == starlette.status.HTTP_404_NOT_FOUND
    user_articles_response = await async_client.get(
        f"/users/{user_id}/articles"
    )
    assert user_articles_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )


@pytest.mark.asyncio
async def test_user_update_requires_payload(async_client):
    create_response = await async_client.post(
        "/users",
        json={
            "user_name": "Payload Tester",
            "email": "payload@example.com",
        },
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    user_id = create_response.json()["user_id"]

    update_response = await async_client.put(
        f"/users/{user_id}",
        json={},
    )
    assert update_response.status_code == (
        starlette.status.HTTP_400_BAD_REQUEST
    )
    assert (
        update_response.json()["detail"]
        == "更新項目を指定してください。"
    )


@pytest.mark.asyncio
async def test_user_update_missing_user_returns_404(async_client):
    update_response = await async_client.put(
        "/users/999",
        json={
            "user_name": "Ghost User",
            "email": "ghost@example.com",
        },
    )
    assert update_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        update_response.json()["detail"] == "ユーザーが見つかりません。"
    )


@pytest.mark.asyncio
async def test_user_delete_missing_returns_404(async_client):
    delete_response = await async_client.delete("/users/999")
    assert delete_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        delete_response.json()["detail"] == "ユーザーが見つかりません。"
    )
