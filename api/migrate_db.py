import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from api.db.db import Base

# TODO: 一時的に環境変数使ってるが、この後変える
load_dotenv()

# TODO: rootで入ってて権限強すぎるので、この後権限変更する
PWD = os.environ["MYSQL_ROOT_PASSWORD"]
DB_URL = f"mysql+pymysql://root:{PWD}@tfk-db:3306/tfk-db?charset=utf8"

engine = create_engine(DB_URL, echo=True)


def reset_database():
    import api.models  # noqa: F401  # モデルをmetadataに登録
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
