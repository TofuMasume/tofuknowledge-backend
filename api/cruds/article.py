from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.articles import Article
from api.schemas.article import ArticleCreate, ArticleUpdate

ACTIVE_DELETED_AT = datetime(2999, 12, 31, 23, 59, 59)


async def list_articles(db: AsyncSession) -> Sequence[Article]:
    """アクティブな記事一覧を取得"""
    result = await db.execute(
        select(Article)
        .where(Article.deleted_at == ACTIVE_DELETED_AT)
        .order_by(Article.created_at.desc())
    )
    return result.scalars().all()


async def get_article(db: AsyncSession, article_id: int) -> Optional[Article]:
    """記事を1件取得。削除済みの場合はNone"""
    article = await db.get(Article, article_id)
    if article is None:
        return None
    if article.deleted_at != ACTIVE_DELETED_AT:
        return None
    return article


async def create_article(
    db: AsyncSession, article_body: ArticleCreate
) -> Article:
    """記事を新規作成"""
    now = datetime.now()
    article = Article(
        author_id=article_body.author_id,
        path=article_body.title,
        summary=article_body.summary,
        created_at=now,
        updated_at=now,
        deleted_at=ACTIVE_DELETED_AT,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


async def update_article(
    db: AsyncSession,
    article_id: int,
    article_body: ArticleUpdate,
) -> Optional[Article]:
    """記事情報を更新"""
    article = await get_article(db, article_id)
    if article is None:
        return None

    has_changes = False
    if article_body.author_id != article.author_id:
        article.author_id = article_body.author_id
        has_changes = True

    if article_body.title is not None:
        article.path = article_body.title
        has_changes = True

    if article_body.summary is not None:
        article.summary = article_body.summary
        has_changes = True

    if has_changes:
        article.updated_at = datetime.now()
        await db.commit()
        await db.refresh(article)

    return article


async def delete_article(
    db: AsyncSession, article_id: int
) -> Optional[Article]:
    """記事を論理削除"""
    article = await get_article(db, article_id)
    if article is None:
        return None

    now = datetime.now()
    article.deleted_at = now
    article.updated_at = now
    await db.commit()
    await db.refresh(article)
    return article


async def touch_article(db: AsyncSession, article: Article) -> Article:
    """記事の最終更新日時のみ更新"""
    article.updated_at = datetime.now()
    await db.commit()
    await db.refresh(article)
    return article
