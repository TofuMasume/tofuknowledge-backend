from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from api.db.db import Base
from api.settings import get_settings

settings = get_settings()

query = {}
if settings.db_charset:
    query["charset"] = settings.db_charset

DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.db_user,
    password=settings.db_password or None,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    query=query,
)

engine = create_engine(DB_URL, echo=settings.db_echo)


def reset_database():
    import api.models  # noqa: F401  # モデルをmetadataに登録
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
