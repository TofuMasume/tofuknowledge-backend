from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.article as article_schema
import api.schemas.user as user_schema
from api.cruds import user as user_crud
from api.db.db import get_db
from api.models.users import User

router = APIRouter()


def _user_to_summary(user: User) -> user_schema.UserSummary:
    return user_schema.UserSummary(
        user_id=user.user_id,
        user_name=user.user_name,
    )


def _user_to_detail(user: User) -> user_schema.UserDetail:
    return user_schema.UserDetail(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        created_at=user.created_at,
    )


def _user_to_create_response(user: User) -> user_schema.UserCreateResponse:
    return user_schema.UserCreateResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        created_at=user.created_at,
    )


def _user_to_update_response(user: User) -> user_schema.UserUpdateResponse:
    return user_schema.UserUpdateResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        created_at=user.created_at,
    )


@router.get("/users", response_model=List[user_schema.UserSummary])
async def list_users(db: AsyncSession = Depends(get_db)):
    """ユーザー一覧/基本情報取得"""
    users = await user_crud.list_users(db)
    return [_user_to_summary(user) for user in users]


@router.get("/users/{user_id}", response_model=user_schema.UserDetail)
async def get_user_detail(
    user_id: int, db: AsyncSession = Depends(get_db)
):
    """user_idのユーザー詳細取得"""
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません。",
        )
    return _user_to_detail(user)


@router.get(
    "/users/{user_id}/articles",
    response_model=List[article_schema.ArticleSummary],
)
async def get_user_articles(
    user_id: int, db: AsyncSession = Depends(get_db)
):
    """user_idに紐づいてるarticlesの基本情報をリスト化"""
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません。",
        )

    articles = await user_crud.list_articles_for_user(db, user_id)
    return [
        article_schema.ArticleSummary(
            title=article.path,
            article_id=article.article_id,
            author_id=article.author_id,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )
        for article in articles
    ]


@router.post(
    "/users",
    response_model=user_schema.UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_body: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """新規ユーザー作成"""
    user = await user_crud.create_user(db, user_body)
    return _user_to_create_response(user)


@router.put(
    "/users/{user_id}",
    response_model=user_schema.UserUpdateResponse,
)
async def edit_user(
    user_id: int,
    user_body: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """user_idのユーザーデータ編集"""
    if (
        user_body.user_name is None
        and user_body.email is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新項目を指定してください。",
        )

    user = await user_crud.update_user(db, user_id, user_body)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません。",
        )
    return _user_to_update_response(user)


@router.delete(
    "/users/{user_id}", response_model=user_schema.UserDeleteResponse
)
async def delete_user(
    user_id: int, db: AsyncSession = Depends(get_db)
):
    """ユーザー削除"""
    user = await user_crud.delete_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません。",
        )
    return user_schema.UserDeleteResponse(
        user_id=user.user_id,
        deleted_at=user.deleted_at,
    )
