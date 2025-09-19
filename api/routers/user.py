from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
async def list_users():
    """ユーザー一覧/基本情報取得
    """
    pass


@router.get("/users/{user_id}")
async def get_user_detail():
    """user_idのユーザー詳細取得
    """
    pass


@router.get("/users/{user_id}/articles")
async def get_user_articles():
    """user_idに紐づいてるarticlesの基本情報をリスト化
    """
    pass


@router.post("/users")
async def create_user():
    """新規ユーザー作成
    """
    pass


@router.put("/users/{user_id}")
async def edit_user():
    """user_idのユーザーデータ編集
    """
    pass


@router.delete("/users/{user_id}")
async def delete_user():
    """ユーザー削除
    """
    pass
