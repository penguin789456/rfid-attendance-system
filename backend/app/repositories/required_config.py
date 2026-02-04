"""規則配置快照資料存取層。"""

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.required_config import RequiredConfig
from app.repositories.base import BaseRepository


class RequiredConfigRepository(BaseRepository[RequiredConfig]):
    """規則配置快照 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(RequiredConfig, db)

    async def get_effective_config(
        self, dept_guid: str, active_day: int, target_date: date
    ) -> RequiredConfig | None:
        """取得指定日期的有效規則配置。"""
        result = await self.db.execute(
            select(RequiredConfig).where(
                and_(
                    RequiredConfig.Dept_GUID == dept_guid,
                    RequiredConfig.ActiveDay == active_day,
                    RequiredConfig.EffectiveFrom <= target_date,
                    (
                        (RequiredConfig.EffectiveTo == None)  # noqa: E711
                        | (RequiredConfig.EffectiveTo >= target_date)
                    ),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_current_config_for_department(
        self, dept_guid: str, weekday: int, target_date: date
    ) -> RequiredConfig | None:
        """取得部門當前有效的規則配置（包含全年）。"""
        # 先找特定星期幾
        config = await self.get_effective_config(dept_guid, weekday, target_date)
        if config:
            return config

        # 找全年配置 (ActiveDay = 8)
        return await self.get_effective_config(dept_guid, 8, target_date)

    async def expire_config(self, config: RequiredConfig, expire_date: date) -> None:
        """使規則配置失效。"""
        config.EffectiveTo = expire_date
        await self.update(config)
