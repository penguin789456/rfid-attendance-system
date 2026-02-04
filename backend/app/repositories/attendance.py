"""考勤資料存取層。"""

from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceDaily
from app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[AttendanceDaily]):
    """考勤 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(AttendanceDaily, db)

    async def get_by_employee_and_date(
        self, rfid_id: str, work_date: date
    ) -> AttendanceDaily | None:
        """取得員工指定日期的考勤記錄。"""
        result = await self.db.execute(
            select(AttendanceDaily).where(
                and_(
                    AttendanceDaily.RFID_ID == rfid_id,
                    AttendanceDaily.WorkDate == work_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_employee_date_range(
        self,
        rfid_id: str,
        start_date: date,
        end_date: date,
    ) -> list[AttendanceDaily]:
        """取得員工在指定日期範圍內的考勤記錄。"""
        result = await self.db.execute(
            select(AttendanceDaily)
            .where(
                and_(
                    AttendanceDaily.RFID_ID == rfid_id,
                    AttendanceDaily.WorkDate >= start_date,
                    AttendanceDaily.WorkDate <= end_date,
                )
            )
            .order_by(AttendanceDaily.WorkDate)
        )
        return list(result.scalars().all())

    async def get_by_date(self, work_date: date) -> list[AttendanceDaily]:
        """取得指定日期所有員工的考勤記錄。"""
        result = await self.db.execute(
            select(AttendanceDaily).where(AttendanceDaily.WorkDate == work_date)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """取得考勤記錄總數。"""
        result = await self.db.execute(
            select(func.count()).select_from(AttendanceDaily)
        )
        return result.scalar_one()
