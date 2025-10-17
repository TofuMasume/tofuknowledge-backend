import pytest
import starlette.status


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
