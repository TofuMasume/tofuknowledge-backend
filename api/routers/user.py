from datetime import datetime
from typing import List

from fastapi import APIRouter

import api.schemas.user as user_schema

router = APIRouter()


@router.get("/users", response_model=List[user_schema.UserSummary])
async def list_users():
    """ユーザー一覧/基本情報取得"""
    return [user_schema.UserSummary(user_id=1, user_name="Tofu Masume")]


@router.get("/users/{user_id}", response_model=user_schema.UserDetail)
async def get_user_detail():
    """user_idのユーザー詳細取得"""
    return user_schema.UserDetail(
        user_id=1,
        user_name="Tofu Masume",
        email="tofu@sample.com",
        created_at=datetime.now(),
    )


@router.get("/users/{user_id}/articles")
async def get_user_articles():
    """user_idに紐づいてるarticlesの基本情報をリスト化"""
    pass


@router.post("/users", response_model=user_schema.UserCreateResponse)
async def create_user():
    """新規ユーザー作成"""
    return user_schema.UserCreateResponse(
        user_id=1,
        user_name="Tofu Masume",
        created_at=datetime.now(),
        email="sample@sample.com",
    )


@router.put("/users/{user_id}")
async def edit_user():
    """user_idのユーザーデータ編集"""
    pass


@router.delete(
    "/users/{user_id}", response_model=user_schema.UserDeleteResponse
)
async def delete_user(user_id: int):
    """ユーザー削除"""
    return user_schema.UserDeleteResponse(user_id=1, deleted_at=datetime.now())
