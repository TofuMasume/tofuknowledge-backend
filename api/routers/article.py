import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, responses, status

import api.schemas.article as article_schema

router = APIRouter()
ARTICLE_STORAGE_DIR = (
    Path(__file__).resolve().parents[2] / "storage" / "articles"
)


def _ensure_storage_dir() -> None:
    ARTICLE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _find_article_file(article_id: int) -> Optional[Path]:
    if not ARTICLE_STORAGE_DIR.exists():
        return None
    for candidate in ARTICLE_STORAGE_DIR.glob(f"{article_id}.*"):
        if candidate.is_file():
            return candidate
    return None


@router.get("/articles", response_model=List[article_schema.ArticleSummary])
async def list_articles():
    """記事一覧取得"""
    return [
        article_schema.ArticleSummary(
            title="article 0",
            article_id=0,
            author_id=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        article_schema.ArticleSummary(
            title="article 1",
            article_id=1,
            author_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]


@router.get(
    "/articles/{article_id}", response_model=article_schema.ArticleDetail
)
async def get_article_details(article_id: int):
    """article_idの記事を取得"""
    now = datetime.now()
    return article_schema.ArticleDetail(
        title=f"article {article_id}",
        article_id=article_id,
        author_id=article_id,
        created_at=now,
        updated_at=now,
    )


@router.post("/articles", response_model=article_schema.ArticleCreateResponse)
async def post_article(article_body: article_schema.ArticleCreate):
    """新規記事投稿
    markdown
    """
    return article_schema.ArticleCreateResponse(
        article_id=1,
        created_at=datetime.now(),
        **article_body.model_dump(),
    )


@router.put(
    "/articles/{article_id}", response_model=article_schema.ArticleUpdate
)
async def edit_article(article_id: int):
    """記事編集"""
    return article_schema.ArticleUpdateResponse(
        updated_at=datetime.now(), article_id=article_id, author_id=1
    )


@router.delete(
    "/articles/{article_id}", response_model=article_schema.ArticleDelete
)
async def delete_article(article_id: int):
    """記事削除"""
    return article_schema.ArticleDelete(article_id=article_id)


@router.post(
    "/articles/{article_id}/file",
    response_model=article_schema.ArticleFileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_article_file(
    article_id: int, file: UploadFile = File(...)
):
    """記事ファイルのアップロード"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイル名を指定してください。",
        )

    _ensure_storage_dir()
    for existing in ARTICLE_STORAGE_DIR.glob(f"{article_id}.*"):
        if existing.is_file():
            existing.unlink()

    suffix = Path(file.filename).suffix or ".bin"
    destination = ARTICLE_STORAGE_DIR / f"{article_id}{suffix}"
    content_type = file.content_type or ""

    try:
        with destination.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ファイルの保存に失敗しました。",
        ) from None
    finally:
        await file.close()

    media_type = (
        content_type or mimetypes.guess_type(destination.name)[0] or
        "application/octet-stream"
    )
    uploaded_at = datetime.now()
    return article_schema.ArticleFileUploadResponse(
        article_id=article_id,
        filename=destination.name,
        content_type=media_type,
        uploaded_at=uploaded_at,
    )


@router.get("/articles/{article_id}/file")
async def download_article_file(article_id: int):
    """記事ファイルのダウンロード"""
    article_file = _find_article_file(article_id)
    if article_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事ファイルが見つかりません。",
        )

    media_type = (
        mimetypes.guess_type(article_file.name)[0]
        or "application/octet-stream"
    )
    return responses.FileResponse(
        article_file, filename=article_file.name, media_type=media_type
    )


@router.get("/articles/{article_id}/tags", tags=["tags"])
async def get_article_tag():
    """article_idに対して紐づいてるタグを取得"""
    pass


@router.post("/articles/{article_id}/tags/{tag_id}", tags=["tags"])
async def add_article_tag():
    """article_idに対して{tag_id}タグ追加"""
    pass


@router.delete("/articles/{article_id}/tags/{tag_id}", tags=["tags"])
async def delete_article_tag():
    """article_idに対して{tag_id}タグ削除"""
    pass
