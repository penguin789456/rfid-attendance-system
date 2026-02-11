"""考勤 API 路由。"""

from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attendance import AttendanceDaily
from app.schemas.attendance import AttendanceDailyResponse, AttendanceDailyUpdate
from app.services.attendance import AttendanceService

router = APIRouter(prefix="/api/attendance-daily", tags=["attendance"])


@router.get("", response_model=list[AttendanceDailyResponse])
async def get_attendance_records(
    skip: int = 0,
    limit: int = 100,
    work_date: date | None = Query(None, description="篩選指定日期的考勤記錄"),
    rfid_id: str | None = Query(None, description="篩選指定員工的考勤記錄"),
    db: AsyncSession = Depends(get_db),
) -> list[AttendanceDaily]:
    """取得考勤記錄列表。"""
    service = AttendanceService(db)
    return await service.get_all(
        skip=skip, limit=limit, work_date=work_date, rfid_id=rfid_id
    )


@router.get("/{guid}", response_model=AttendanceDailyResponse)
async def get_attendance_record(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> AttendanceDaily:
    """取得單一考勤記錄。"""
    service = AttendanceService(db)
    return await service.get_by_id(guid)


@router.put("/{guid}", response_model=AttendanceDailyResponse)
async def update_attendance_record(
    guid: str,
    data: AttendanceDailyUpdate,
    db: AsyncSession = Depends(get_db),
) -> AttendanceDaily:
    """更新考勤記錄。"""
    service = AttendanceService(db)
    return await service.update_attendance(guid, data)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance_record(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除考勤記錄。"""
    service = AttendanceService(db)
    await service.delete_attendance(guid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
