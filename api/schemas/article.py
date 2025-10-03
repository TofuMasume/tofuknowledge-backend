from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# NOTE: ちょっと気になったので...さっきまでレスポンスのスキーマにpath含めてたんだけど、
# NOTE: 内部構造明かすことになって危ないんじゃないか？となったので消した。
# TODO: おそらくpath情報とかはmodelsのほうに入れるべきなので忘れないで！

# GET用 schema


class ArticleSummary(BaseModel):
    """article基本情報"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(examples=["typing"])
    article_id: int
    author_id: int


class ArticleDetail(ArticleSummary):
    """article詳細情報"""

    created_at: datetime
    updated_at: datetime


# POST schema


class ArticleCreate(BaseModel):
    """article作成時に渡してほしい"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(examples=["typing"])
    summary: Optional[str] = Field(examples=["typingの説明"])
    author_id: int


class ArticleCreateResponse(ArticleCreate):
    """article作成後のレスポンス"""

    title: str = Field(examples=["typing"])
    article_id: int
    created_at: datetime
