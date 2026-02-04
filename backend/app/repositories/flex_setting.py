"""彈性設定資料存取層。"""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flex_setting import FlexSetting
from app.repositories.base import BaseRepository


class FlexSettingRepository(BaseRepository[FlexSetting]):
    """彈性設定 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(FlexSetting, db)

    async def get_all_active(
        self, skip: int = 0, limit: int = 100
    ) -> list[FlexSetting]:
        """取得所有未刪除的彈性設定。"""
        result = await self.db.execute(
            select(FlexSetting)
            .where(FlexSetting.IsDeleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_department(self, dept_guid: str) -> FlexSetting | None:
        """根據部門取得彈性設定。"""
        result = await self.db.execute(
            select(FlexSetting).where(
                and_(
                    FlexSetting.Dept_GUID == dept_guid,
                    FlexSetting.IsDeleted == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def soft_delete(
        self, flex_setting: FlexSetting, deleted_by: str
    ) -> FlexSetting:
        """軟刪除彈性設定。"""
        from datetime import datetime

        flex_setting.IsDeleted = True
        flex_setting.DeletedTime = datetime.utcnow()
        flex_setting.DeletedBy = deleted_by
        return await self.update(flex_setting)
