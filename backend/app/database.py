"""資料庫連線配置。"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎模型類別。"""

    pass


async def get_db() -> AsyncSession:
    """取得資料庫 session。"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """初始化資料庫，建立所有資料表。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
