from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from api.settings import get_settings

settings = get_settings()

query = {}
if settings.db_charset:
    query["charset"] = settings.db_charset

ASYNC_DB_URL = URL.create(
    drivername="mysql+aiomysql",
    username=settings.db_user,
    password=settings.db_password or None,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    query=query,
)

async_engine = create_async_engine(ASYNC_DB_URL, echo=settings.db_echo)
async_session = sessionmaker(
    expire_on_commit=False,
    bind=async_engine,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session
