import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# TODO: 一時的に環境変数使ってるが、この後変える
load_dotenv()

# TODO: rootで入ってて権限強すぎるので、この後権限変更する。
PWD = os.environ["MYSQL_ROOT_PASSWORD"]
ASYNC_DB_URL = f"mysql+aiomysql:{PWD}//root:@db:3306/tfk-db?charset=utf8"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = sessionmaker(
    expire_on_commit=False,
    bind=async_engine,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session
