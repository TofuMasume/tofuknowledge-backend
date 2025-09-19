from fastapi import FastAPI

from api.routers import article, tag, user

description = """
## articles
記事関連
## tags
タグ関連
## users
ユーザー関連
"""

tags_metadata = [
    {
        "name": "articles",
        "description": "記事に関する操作"
    },
    {
        "name": "tags",
        "description": "タグに関する操作"
    },
    {
        "name": "users",
        "description": "ユーザーに関する操作"
    }
]

app = FastAPI(
    title="TofuKnowledge API",
    summary="記事を投稿したり取得したり",
    description=description,
    version="0.1.0",
    contact={
        "name": "Tofu Masume",
        "url": "https://x.com/tofu_vr"
    }
    )

app.include_router(article.router, tags=["articles"])
app.include_router(tag.router, tags=["tags"])
app.include_router(user.router, tags=["users"])
