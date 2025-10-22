from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

import api.models  # noqa: F401  # モデルのマッパーを登録するために必要
from api.routers import article, tag, user
from api.settings import get_settings

# API keyの処理
settings = get_settings()
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


def verify_token(auth_header: str = Depends(api_key_header)):
    header_value = auth_header.strip()

    token = header_value
    if " " in header_value:
        scheme, _, credentials = header_value.partition(" ")
        if scheme.lower() != "bearer" or not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication token",
            )
        token = credentials.strip()

    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token",
        )


description = """
## articles
記事関連
## tags
タグ関連
## users
ユーザー関連
"""

tags_metadata = [
    {"name": "articles", "description": "記事に関する操作"},
    {"name": "tags", "description": "タグに関する操作"},
    {"name": "users", "description": "ユーザーに関する操作"},
]

app = FastAPI(
    title="TofuKnowledge API",
    summary="記事を投稿したり取得したり",
    description=description,
    version="0.1.0",
    contact={"name": "Tofu Masume", "url": "https://x.com/tofu_vr"},
    dependencies=[Depends(verify_token)],
)

app.include_router(article.router, tags=["articles"])
app.include_router(tag.router, tags=["tags"])
app.include_router(user.router, tags=["users"])
