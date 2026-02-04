"""班表資料存取層。"""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import Schedule
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    """班表 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(Schedule, db)

    async def get_all_active(self, skip: int = 0, limit: int = 100) -> list[Schedule]:
        """取得所有未刪除的班表。"""
        result = await self.db.execute(
            select(Schedule)
            .where(Schedule.IsDeleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_department(
        self, dept_guid: str, active_only: bool = True
    ) -> list[Schedule]:
        """根據部門取得班表列表。"""
        conditions = [Schedule.Dept_GUID == dept_guid]
        if active_only:
            conditions.append(Schedule.IsDeleted == False)  # noqa: E712

        result = await self.db.execute(select(Schedule).where(and_(*conditions)))
        return list(result.scalars().all())

    async def get_by_department_and_day(
        self, dept_guid: str, active_day: int
    ) -> Schedule | None:
        """根據部門和日期取得班表。"""
        result = await self.db.execute(
            select(Schedule).where(
                and_(
                    Schedule.Dept_GUID == dept_guid,
                    Schedule.ActiveDay == active_day,
                    Schedule.IsDeleted == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_schedule_for_date(
        self, dept_guid: str, weekday: int
    ) -> Schedule | None:
        """取得部門在指定星期幾的班表（包含全年班表）。"""
        # 先找特定星期幾的班表
        schedule = await self.get_by_department_and_day(dept_guid, weekday)
        if schedule:
            return schedule

        # 找全年班表 (ActiveDay = 8)
        return await self.get_by_department_and_day(dept_guid, 8)

    async def soft_delete(self, schedule: Schedule, deleted_by: str) -> Schedule:
        """軟刪除班表。"""
        from datetime import datetime

        schedule.IsDeleted = True
        schedule.DeletedTime = datetime.utcnow()
        schedule.DeletedBy = deleted_by
        return await self.update(schedule)
