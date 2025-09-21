from datetime import datetime
from typing import List

from fastapi import APIRouter

import api.schemas.article as article_schema

router = APIRouter()


@router.get("/articles")
async def list_articles():
    """記事一覧/基本情報取得"""
    pass


@router.get(
    "/articles/{article_id}", response_model=List[article_schema.Article]
)
async def get_article_details():
    """article_idの記事詳細取得"""
    return [
        article_schema.Article(
            id=1,
            user_id=1,
            path="/hoge/fuga/",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            summary="test article",
        )
    ]


@router.post("/articles")
async def post_article():
    """新規記事投稿
    markdown
    """
    pass


@router.put("/articles/{article_id}")
async def edit_article():
    """記事編集"""
    pass


@router.delete("/articles/{article_id}")
async def delete_article():
    """記事削除"""
    pass


@router.get("/articles/{article_id}/tags", tags=["tags"])
async def get_article_tag():
    """article_idに対して紐づいてるタグを取得"""
    pass


@router.post("/articles/{article_id}/tags/{tag_id}", tags=["tags"])
async def add_article_tag():
    """article_idに対して{tag_id}タグ追加"""
    pass


@router.delete("/articles/{article_id}/tags/{tag_id}", tags=["tags"])
async def delete_article_tag():
    """article_idに対して{tag_id}タグ削除"""
    pass
