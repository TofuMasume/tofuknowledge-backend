import os

os.environ.setdefault("API_KEY", "test-secret")
os.environ.setdefault("DB_USER", "test_app")
os.environ.setdefault("DB_PASSWORD", "test-password")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import api.models  # noqa: F401  # モデルをmetadataに登録
from api.db.db import Base, get_db
from api.main import app
from api.settings import get_settings

settings = get_settings()
ASYNC_DB_URL = settings.test_db_url
AUTHORIZATION_HEADER_VALUE = f"Bearer {settings.api_key}"


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:  # type: ignore
    """FastAPIアプリに対するHTTPクライアント（SQLite in-memory使用）"""
    async_engine = create_async_engine(
        ASYNC_DB_URL, echo=settings.db_echo
    )
    async_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": AUTHORIZATION_HEADER_VALUE},
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
