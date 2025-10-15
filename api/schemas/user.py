from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# GET schema
class UserSummary(BaseModel):
    """user基本情報"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(examples=[1])
    user_name: str = Field(examples=["Tofu Masume"])


class UserDetail(UserSummary):
    """user詳細情報"""

    email: str
    created_at: datetime


# POST schema
class UserCreate(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    user_name: str
    email: str


class UserCreateResponse(UserCreate):

    user_id: int
    created_at: datetime


# DELETE schema
class UserDelete(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    user_id: int


class UserDeleteResponse(UserDelete):

    deleted_at: datetime
