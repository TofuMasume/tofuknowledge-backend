from pydantic import BaseModel, ConfigDict, Field


class TagSummary(BaseModel):
    """タグの基本情報"""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int = Field(examples=[1])
    tag_name: str = Field(examples=["Python"])


class TagDetail(TagSummary):
    """タグ詳細情報"""

    pass


class TagCreate(BaseModel):
    """タグ作成時の入力"""

    model_config = ConfigDict(from_attributes=True)

    tag_name: str


class TagCreateResponse(TagDetail):
    """タグ作成時のレスポンス"""

    pass


class TagUpdate(BaseModel):
    """タグ更新時の入力"""

    model_config = ConfigDict(from_attributes=True)

    tag_name: str | None = Field(default=None, examples=["Updated Tag"])


class TagUpdateResponse(TagDetail):
    """タグ更新時のレスポンス"""

    pass


class TagDeleteResponse(BaseModel):
    """タグ削除時のレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    tag_id: int
