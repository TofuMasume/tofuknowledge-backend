import pytest
import starlette.status


@pytest.mark.asyncio
async def test_tag_crud_flow(async_client):
    # 初期状態はタグなし
    list_response = await async_client.get("/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == []

    # タグ作成
    create_response = await async_client.post(
        "/tags",
        json={"tag_name": "Python"},
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    created = create_response.json()
    assert created["tag_name"] == "Python"
    tag_id = created["tag_id"]

    # 作成済みタグを一覧から取得
    list_response = await async_client.get("/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    tags = list_response.json()
    assert len(tags) == 1
    assert tags[0]["tag_id"] == tag_id
    assert tags[0]["tag_name"] == "Python"

    # タグ詳細取得
    detail_response = await async_client.get(f"/tags/{tag_id}")
    assert detail_response.status_code == starlette.status.HTTP_200_OK
    assert detail_response.json()["tag_name"] == "Python"

    # タグ名更新
    update_response = await async_client.put(
        f"/tags/{tag_id}",
        json={"tag_name": "FastAPI"},
    )
    assert update_response.status_code == starlette.status.HTTP_200_OK
    updated = update_response.json()
    assert updated["tag_name"] == "FastAPI"

    # 更新結果を詳細で確認
    detail_response = await async_client.get(f"/tags/{tag_id}")
    assert detail_response.status_code == starlette.status.HTTP_200_OK
    assert detail_response.json()["tag_name"] == "FastAPI"

    # タグ削除
    delete_response = await async_client.delete(f"/tags/{tag_id}")
    assert delete_response.status_code == starlette.status.HTTP_200_OK
    assert delete_response.json() == {"tag_id": tag_id}

    # 削除後の一覧
    list_response = await async_client.get("/tags")
    assert list_response.status_code == starlette.status.HTTP_200_OK
    assert list_response.json() == []

    # 削除済みタグの詳細は404
    detail_response = await async_client.get(f"/tags/{tag_id}")
    assert detail_response.status_code == starlette.status.HTTP_404_NOT_FOUND
    assert detail_response.json()["detail"] == "タグが見つかりません。"


@pytest.mark.asyncio
async def test_tag_create_conflict(async_client):
    create_response = await async_client.post(
        "/tags",
        json={"tag_name": "Python"},
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED

    conflict_response = await async_client.post(
        "/tags",
        json={"tag_name": "Python"},
    )
    assert conflict_response.status_code == starlette.status.HTTP_409_CONFLICT
    assert (
        conflict_response.json()["detail"]
        == "同名のタグが既に存在します。"
    )


@pytest.mark.asyncio
async def test_tag_update_requires_name(async_client):
    create_response = await async_client.post(
        "/tags",
        json={"tag_name": "NoUpdate"},
    )
    assert create_response.status_code == starlette.status.HTTP_201_CREATED
    tag_id = create_response.json()["tag_id"]

    update_response = await async_client.put(
        f"/tags/{tag_id}",
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
async def test_tag_update_missing_tag_returns_404(async_client):
    update_response = await async_client.put(
        "/tags/999",
        json={"tag_name": "Unknown"},
    )
    assert update_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        update_response.json()["detail"] == "タグが見つかりません。"
    )


@pytest.mark.asyncio
async def test_tag_update_conflict_returns_409(async_client):
    python_response = await async_client.post(
        "/tags",
        json={"tag_name": "Python"},
    )
    assert python_response.status_code == starlette.status.HTTP_201_CREATED

    fastapi_response = await async_client.post(
        "/tags",
        json={"tag_name": "FastAPI"},
    )
    assert fastapi_response.status_code == starlette.status.HTTP_201_CREATED
    fastapi_id = fastapi_response.json()["tag_id"]

    conflict_response = await async_client.put(
        f"/tags/{fastapi_id}",
        json={"tag_name": "Python"},
    )
    assert conflict_response.status_code == (
        starlette.status.HTTP_409_CONFLICT
    )
    assert (
        conflict_response.json()["detail"]
        == "同名のタグが既に存在します。"
    )


@pytest.mark.asyncio
async def test_tag_delete_missing_returns_404(async_client):
    delete_response = await async_client.delete("/tags/999")
    assert delete_response.status_code == (
        starlette.status.HTTP_404_NOT_FOUND
    )
    assert (
        delete_response.json()["detail"] == "タグが見つかりません。"
    )
