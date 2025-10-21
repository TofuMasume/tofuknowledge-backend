from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.tag as tag_schema
from api.db.db import get_db
from api.models.article_tag import ArticleTag
from api.models.tags import Tag

router = APIRouter()


def _tag_to_summary(tag: Tag) -> tag_schema.TagSummary:
    return tag_schema.TagSummary(
        tag_id=tag.tag_id,
        tag_name=tag.tag_name,
    )


def _tag_to_detail(tag: Tag) -> tag_schema.TagDetail:
    return tag_schema.TagDetail(
        tag_id=tag.tag_id,
        tag_name=tag.tag_name,
    )


@router.get("/tags", response_model=List[tag_schema.TagSummary])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """タグ一覧/基本情報取得"""
    result = await db.execute(select(Tag).order_by(Tag.tag_id))
    tags = result.scalars().all()
    return [_tag_to_summary(tag) for tag in tags]


@router.post(
    "/tags",
    response_model=tag_schema.TagCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_body: tag_schema.TagCreate, db: AsyncSession = Depends(get_db)
):
    """タグ作成"""
    tag = Tag(tag_name=tag_body.tag_name)
    db.add(tag)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="同名のタグが既に存在します。",
        ) from exc
    await db.refresh(tag)
    return _tag_to_detail(tag)


@router.get("/tags/{tag_id}", response_model=tag_schema.TagDetail)
async def get_tag_detail(
    tag_id: int, db: AsyncSession = Depends(get_db)
):
    """タグ詳細取得"""
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タグが見つかりません。",
        )
    return _tag_to_detail(tag)


@router.put(
    "/tags/{tag_id}",
    response_model=tag_schema.TagUpdateResponse,
)
async def edit_tag(
    tag_id: int,
    tag_body: tag_schema.TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    """タグ編集"""
    if tag_body.tag_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新項目を指定してください。",
        )

    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タグが見つかりません。",
        )

    tag.tag_name = tag_body.tag_name
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="同名のタグが既に存在します。",
        ) from exc
    await db.refresh(tag)
    return tag_schema.TagUpdateResponse(
        tag_id=tag.tag_id,
        tag_name=tag.tag_name,
    )


@router.delete(
    "/tags/{tag_id}",
    response_model=tag_schema.TagDeleteResponse,
)
async def delete_tag(
    tag_id: int, db: AsyncSession = Depends(get_db)
):
    """タグ削除"""
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タグが見つかりません。",
        )

    await db.execute(
        delete(ArticleTag).where(ArticleTag.tag_id == tag.tag_id)
    )
    await db.delete(tag)
    await db.commit()
    return tag_schema.TagDeleteResponse(tag_id=tag_id)
