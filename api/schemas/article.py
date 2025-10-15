from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# NOTE: ちょっと気になったので...さっきまでレスポンスのスキーマにpath含めてたんだけど、
# NOTE: 内部構造明かすことになって危ないんじゃないか？となったので消した。
# TODO: おそらくpath情報とかはmodelsのほうに入れるべきなので忘れないで！


# GET schema
class ArticleSummary(BaseModel):
    """article基本情報"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(examples=["typing"])
    article_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


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
    author_id: int = Field(examples=[1])


class ArticleCreateResponse(ArticleCreate):
    """article作成後のレスポンス"""

    title: str = Field(examples=["typing"])
    article_id: int = Field(examples=[1])
    created_at: datetime


# PUT schema
class ArticleUpdate(BaseModel):
    """article編集時にほしい"""

    model_config = ConfigDict(from_attributes=True)

    article_id: int = Field(examples=[1])
    author_id: int = Field(examples=[1])


class ArticleUpdateResponse(ArticleUpdate):
    """article編集後のレスポンス"""

    updated_at: datetime


# DELETE schema
class ArticleDelete(BaseModel):
    """article削除時"""

    model_config = ConfigDict(from_attributes=True)

    article_id: int = Field(examples=[1])


class ArticleDeleteResponse(ArticleDelete):
    deleted_at: datetime


class ArticleFileUploadResponse(BaseModel):
    """articleのファイルアップロード後のレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    article_id: int = Field(examples=[1])
    filename: str = Field(examples=["1.md"])
    content_type: str = Field(examples=["text/markdown"])
    uploaded_at: datetime
