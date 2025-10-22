import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_charset: str
    db_echo: bool
    article_storage_dir: Path
    test_db_url: str
    api_key: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parent.parent
    default_storage_dir = project_root / "storage" / "articles"

    db_password = os.getenv("DB_PASSWORD")
    if db_password is None:
        db_password = os.getenv("MYSQL_ROOT_PASSWORD", "")

    api_key = os.getenv("API_KEY")
    if api_key is None or not api_key.strip():
        raise RuntimeError("API_KEY environment variable must be set.")

    return Settings(
        db_user=os.getenv("DB_USER", "root"),
        db_password=db_password,
        db_host=os.getenv("DB_HOST", "tfk-db"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.getenv("DB_NAME", "tfk-db"),
        db_charset=os.getenv("DB_CHARSET", "utf8"),
        db_echo=_get_bool_env("DB_ECHO", True),
        api_key=api_key.strip(),
        article_storage_dir=Path(
            os.getenv("ARTICLE_STORAGE_DIR", str(default_storage_dir))
        ).expanduser(),
        test_db_url=os.getenv("TEST_DB_URL", "sqlite+aiosqlite:///:memory:"),
    )
