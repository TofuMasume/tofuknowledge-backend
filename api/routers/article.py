import mimetypes
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    responses,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.article as article_schema
import api.schemas.tag as tag_schema
from api.cruds import article as article_crud
from api.cruds import user as user_crud
from api.db.db import get_db
from api.models.articles import Article
from api.models.article_tag import ArticleTag
from api.models.tags import Tag

router = APIRouter()
ARTICLE_STORAGE_DIR = (
    Path(__file__).resolve().parents[2] / "storage" / "articles"
)


def _ensure_storage_dir() -> None:
    ARTICLE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _find_article_file(article_id: int) -> Optional[Path]:
    if not ARTICLE_STORAGE_DIR.exists():
        return None
    for candidate in ARTICLE_STORAGE_DIR.glob(f"{article_id}.*"):
        if candidate.is_file():
            return candidate
    return None


def _article_to_summary(article: Article) -> article_schema.ArticleSummary:
    return article_schema.ArticleSummary(
        title=article.path,
        article_id=article.article_id,
        author_id=article.author_id,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def _article_to_detail(article: Article) -> article_schema.ArticleDetail:
    return article_schema.ArticleDetail(
        title=article.path,
        article_id=article.article_id,
        author_id=article.author_id,
        created_at=article.created_at,
        updated_at=article.updated_at,
        summary=article.summary,
    )


def _article_to_create_response(
    article: Article,
) -> article_schema.ArticleCreateResponse:
    return article_schema.ArticleCreateResponse(
        title=article.path,
        summary=article.summary,
        author_id=article.author_id,
        article_id=article.article_id,
        created_at=article.created_at,
    )


def _article_to_update_response(
    article: Article,
) -> article_schema.ArticleUpdateResponse:
    return article_schema.ArticleUpdateResponse(
        article_id=article.article_id,
        author_id=article.author_id,
        title=article.path,
        summary=article.summary,
        updated_at=article.updated_at,
    )


def _tag_to_response(tag: Tag) -> tag_schema.TagRead:
    return tag_schema.TagRead(tag_id=tag.tag_id, tag_name=tag.tag_name)


@router.get("/articles", response_model=List[article_schema.ArticleSummary])
async def list_articles(db: AsyncSession = Depends(get_db)):
    """記事一覧取得"""
    articles = await article_crud.list_articles(db)
    return [_article_to_summary(article) for article in articles]


@router.get(
    "/articles/{article_id}", response_model=article_schema.ArticleDetail
)
async def get_article_details(
    article_id: int, db: AsyncSession = Depends(get_db)
):
    """article_idの記事を取得"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )
    return _article_to_detail(article)


@router.post(
    "/articles",
    response_model=article_schema.ArticleCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_article(
    article_body: article_schema.ArticleCreate,
    db: AsyncSession = Depends(get_db),
):
    """新規記事投稿"""
    author = await user_crud.get_user(db, article_body.author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="著者となるユーザーが見つかりません。",
        )

    article = await article_crud.create_article(db, article_body)
    return _article_to_create_response(article)


@router.put(
    "/articles/{article_id}",
    response_model=article_schema.ArticleUpdateResponse,
)
async def edit_article(
    article_id: int,
    article_body: article_schema.ArticleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """記事編集"""
    if article_body.article_id != article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスと本文のarticle_idが一致しません。",
        )

    if await article_crud.get_article(db, article_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    author = await user_crud.get_user(db, article_body.author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="著者となるユーザーが見つかりません。",
        )

    article = await article_crud.update_article(db, article_id, article_body)
    return _article_to_update_response(article)


@router.delete(
    "/articles/{article_id}",
    response_model=article_schema.ArticleDeleteResponse,
)
async def delete_article(
    article_id: int, db: AsyncSession = Depends(get_db)
):
    """記事削除"""
    article = await article_crud.delete_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )
    return article_schema.ArticleDeleteResponse(
        article_id=article.article_id,
        deleted_at=article.deleted_at,
    )


@router.post(
    "/articles/{article_id}/file",
    response_model=article_schema.ArticleFileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_article_file(
    article_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """記事ファイルのアップロード"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイル名を指定してください。",
        )

    _ensure_storage_dir()
    for existing in ARTICLE_STORAGE_DIR.glob(f"{article_id}.*"):
        if existing.is_file():
            existing.unlink()

    suffix = Path(file.filename).suffix or ".bin"
    destination = ARTICLE_STORAGE_DIR / f"{article_id}{suffix}"
    content_type = file.content_type or ""

    try:
        with destination.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ファイルの保存に失敗しました。",
        ) from None
    finally:
        await file.close()

    media_type = (
        content_type or mimetypes.guess_type(destination.name)[0] or
        "application/octet-stream"
    )
    updated_article = await article_crud.touch_article(db, article)
    uploaded_at = updated_article.updated_at
    return article_schema.ArticleFileUploadResponse(
        article_id=article_id,
        filename=destination.name,
        content_type=media_type,
        uploaded_at=uploaded_at,
    )


@router.get("/articles/{article_id}/file")
async def download_article_file(
    article_id: int, db: AsyncSession = Depends(get_db)
):
    """記事ファイルのダウンロード"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    article_file = _find_article_file(article_id)
    if article_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事ファイルが見つかりません。",
        )

    media_type = (
        mimetypes.guess_type(article_file.name)[0]
        or "application/octet-stream"
    )
    return responses.FileResponse(
        article_file, filename=article_file.name, media_type=media_type
    )


@router.get(
    "/articles/{article_id}/tags",
    tags=["tags"],
    response_model=List[tag_schema.TagRead],
)
async def get_article_tag(
    article_id: int, db: AsyncSession = Depends(get_db)
):
    """article_idに対して紐づいてるタグを取得"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    result = await db.execute(
        select(Tag)
        .join(ArticleTag, Tag.tag_id == ArticleTag.tag_id)
        .where(ArticleTag.article_id == article_id)
        .order_by(Tag.tag_id)
    )
    tags = result.scalars().all()
    return [_tag_to_response(tag) for tag in tags]


@router.post(
    "/articles/{article_id}/tags/{tag_id}",
    tags=["tags"],
    response_model=tag_schema.TagRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_article_tag(
    article_id: int, tag_id: int, db: AsyncSession = Depends(get_db)
):
    """article_idに対して{tag_id}タグ追加"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タグが見つかりません。",
        )

    existing = await db.execute(
        select(ArticleTag).where(
            ArticleTag.article_id == article_id,
            ArticleTag.tag_id == tag_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="タグは既に記事に紐づいています。",
        )

    response_tag = _tag_to_response(tag)
    association = ArticleTag(article_id=article_id, tag_id=tag_id)
    db.add(association)
    await db.commit()
    return response_tag


@router.delete(
    "/articles/{article_id}/tags/{tag_id}",
    tags=["tags"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_article_tag(
    article_id: int, tag_id: int, db: AsyncSession = Depends(get_db)
):
    """article_idに対して{tag_id}タグ削除"""
    article = await article_crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません。",
        )

    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タグが見つかりません。",
        )

    association_result = await db.execute(
        select(ArticleTag).where(
            ArticleTag.article_id == article_id,
            ArticleTag.tag_id == tag_id,
        )
    )
    association = association_result.scalar_one_or_none()
    if association is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事とタグの紐づけが見つかりません。",
        )

    await db.delete(association)
    await db.commit()
