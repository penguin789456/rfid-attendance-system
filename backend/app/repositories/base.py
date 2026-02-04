"""基礎 Repository 類別。"""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """基礎 Repository，提供通用 CRUD 操作。"""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """初始化 Repository。"""
        self.model = model
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """取得所有記錄。"""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(
        self, id_value: str, id_field: str = "GUID"
    ) -> ModelType | None:
        """根據 ID 取得單一記錄。"""
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, id_field) == id_value)
        )
        return result.scalar_one_or_none()

    async def create(self, obj: ModelType) -> ModelType:
        """建立新記錄。"""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """更新記錄。"""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """刪除記錄。"""
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """取得總記錄數。"""
        from sqlalchemy import func

        result = await self.db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
