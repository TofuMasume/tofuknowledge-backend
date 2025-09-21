from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Article(BaseModel):
    title: str = Field(examples=["typing"])
    summary: Optional[str] = Field(examples=["typingの説明"])
    id: int
    user_id: int
    path: str
    created_at: datetime
    updated_at: datetime


class ArticleCreate(BaseModel):
    title: str = Field(examples=["typing"])
    summary: Optional[str] = Field(examples=["typingの説明"])
    user_id: int

    class Config:
        orm_mode = True


class ArticleCreateResponse(ArticleCreate):
    id: int
    path: str
    created_at: datetime
