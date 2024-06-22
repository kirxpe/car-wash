from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncAttrs
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Base(AsyncAttrs, DeclarativeBase):  # тут хранятся все метаданные
    pass


engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
