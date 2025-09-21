from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# GET用 schema


class ArticleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(examples=["typing"])
    summary: Optional[str] = Field(examples=["typingの説明"])
    article_id: int
    user_id: int


class ArticleDetail(ArticleSummary):
    path: str
    created_at: datetime
    updated_at: datetime


# POST schema


class ArticleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(examples=["typing"])
    summary: Optional[str] = Field(examples=["typingの説明"])
    user_id: int


class ArticleCreateResponse(ArticleCreate):
    article_id: int
    path: str
    created_at: datetime
