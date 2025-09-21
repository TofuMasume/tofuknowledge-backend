from fastapi import APIRouter

router = APIRouter()


@router.get("/tags")
async def get_tags():
    """タグ一覧/基本情報取得"""
    pass


@router.post("/tags")
async def create_tag():
    """タグ作成"""
    pass


@router.get("/tags/{tag_id}")
async def get_tag_detail():
    """タグ詳細取得"""
    pass


@router.put("/tags/{tag_id}")
async def edit_tag():
    """タグ編集"""
    pass


@router.delete("/tags/{tag_id}")
async def delete_tag():
    """タグ削除"""
    pass
