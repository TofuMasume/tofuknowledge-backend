from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    id: int
    user_id: int
    path: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = Field(None, examples=["typingの説明"])
