from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """タグの共通情報（作成時など）"""

    tag_name: str = Field(examples=["Python"])


class TagRead(TagBase):
    """タグ取得時の情報"""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int = Field(examples=[1])


class TagCreate(TagBase):
    """タグ作成時の入力"""

    pass


class TagUpdate(BaseModel):
    """タグ更新時の入力"""

    model_config = ConfigDict(from_attributes=True)

    tag_name: str | None = Field(default=None, examples=["Updated Tag"])


class TagDeleteResponse(BaseModel):
    """タグ削除時のレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int
