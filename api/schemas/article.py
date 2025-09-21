from typing import Optional
import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    id: int
    user_id: int
    path: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    summary: str
