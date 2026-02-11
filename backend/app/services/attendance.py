"""考勤業務邏輯服務。"""

from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceDaily
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance import AttendanceDailyUpdate


class AttendanceService:
    """考勤服務，處理考勤記錄 CRUD 邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.attendance_repo = AttendanceRepository(db)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        work_date: date | None = None,
        rfid_id: str | None = None,
    ) -> list[AttendanceDaily]:
        """取得考勤記錄列表（支援篩選）。"""
        if work_date and rfid_id:
            record = await self.attendance_repo.get_by_employee_and_date(
                rfid_id, work_date
            )
            return [record] if record else []
        elif work_date:
            return await self.attendance_repo.get_by_date(work_date)
        elif rfid_id:
            today = date.today()
            start_date = today - timedelta(days=30)
            return await self.attendance_repo.get_by_employee_date_range(
                rfid_id, start_date, today
            )

        return await self.attendance_repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, guid: str) -> AttendanceDaily:
        """取得單一考勤記錄。"""
        record = await self.attendance_repo.get_by_id(guid)
        if not record:
            raise HTTPException(status_code=404, detail="考勤記錄不存在")
        return record

    async def update_attendance(
        self, guid: str, data: AttendanceDailyUpdate
    ) -> AttendanceDaily:
        """更新考勤記錄。"""
        record = await self.attendance_repo.get_by_id(guid)
        if not record:
            raise HTTPException(status_code=404, detail="考勤記錄不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(record, key, value)

        return await self.attendance_repo.update(record)

    async def delete_attendance(self, guid: str) -> None:
        """刪除考勤記錄。"""
        record = await self.attendance_repo.get_by_id(guid)
        if not record:
            raise HTTPException(status_code=404, detail="考勤記錄不存在")

        await self.attendance_repo.delete(record)
