from datetime import datetime
from typing import List

from fastapi import APIRouter

import api.schemas.article as article_schema

router = APIRouter()


@router.get("/articles", response_model=List[article_schema.ArticleSummary])
async def list_articles():
    """記事一覧/基本情報取得"""
    return [
        article_schema.ArticleSummary(
            title="article 0", article_id=0, author_id=0
        ),
        article_schema.ArticleSummary(
            title="article 1", article_id=1, author_id=1
        ),
    ]


@router.get(
    "/articles/{article_id}", response_model=article_schema.ArticleDetail
)
async def get_article_details(article_id: int):
    """article_idの記事詳細取得"""
    return article_schema.ArticleDetail(
        title="test article",
        article_id=article_id,
        author_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.post("/articles", response_model=article_schema.ArticleCreateResponse)
async def post_article(article_body: article_schema.ArticleCreate):
    """新規記事投稿
    markdown
    """
    return article_schema.ArticleCreateResponse(
        article_id=1,
        created_at=datetime.now(),
        **article_body.dict(),
    )


@router.put(
    "/articles/{article_id}", response_model=article_schema.ArticleUpdate
)
async def edit_article(article_id: int):
    """記事編集"""
    return article_schema.ArticleUpdateResponse(
        updated_at=datetime.now(), article_id=article_id, author_id=1
    )


@router.delete(
    "/articles/{article_id}", response_model=article_schema.ArticleDelete
)
async def delete_article(article_id: int):
    """記事削除"""
    return article_schema.ArticleDelete(article_id=datetime)


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
