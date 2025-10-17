from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds.article import list_articles_by_author
from api.models.users import User
from api.schemas.user import UserCreate, UserUpdate


async def list_users(db: AsyncSession) -> Sequence[User]:
    """削除されていないユーザー一覧を取得"""
    result = await db.execute(
        select(User)
        .where(User.deleted_at.is_(None))
        .order_by(User.created_at.asc(), User.user_id.asc())
    )
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """ユーザーを1件取得。削除済みの場合はNone"""
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        return None
    return user


async def create_user(db: AsyncSession, body: UserCreate) -> User:
    """ユーザーを新規作成"""
    user = User(
        user_name=body.user_name,
        email=body.email,
        created_at=datetime.now(),
        deleted_at=None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user_id: int,
    body: UserUpdate,
) -> Optional[User]:
    """ユーザー情報を更新"""
    user = await get_user(db, user_id)
    if user is None:
        return None

    has_changes = False
    if body.user_name is not None and body.user_name != user.user_name:
        user.user_name = body.user_name
        has_changes = True
    if body.email is not None and body.email != user.email:
        user.email = body.email
        has_changes = True

    if has_changes:
        await db.commit()
        await db.refresh(user)

    return user


async def delete_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """ユーザーを論理削除"""
    user = await get_user(db, user_id)
    if user is None:
        return None
    user.deleted_at = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def list_articles_for_user(db: AsyncSession, user_id: int):
    """ユーザーの公開中の記事一覧"""
    return await list_articles_by_author(db, user_id)
