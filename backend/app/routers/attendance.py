"""考勤 API 路由。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attendance import AttendanceDaily
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance import AttendanceDailyResponse, AttendanceDailyUpdate

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
    repo = AttendanceRepository(db)

    if work_date and rfid_id:
        # 取得特定員工特定日期的記錄
        record = await repo.get_by_employee_and_date(rfid_id, work_date)
        return [record] if record else []
    elif work_date:
        # 取得特定日期所有記錄
        return await repo.get_by_date(work_date)
    elif rfid_id:
        # 取得特定員工所有記錄
        from datetime import timedelta

        today = date.today()
        start_date = today - timedelta(days=30)  # 預設最近 30 天
        return await repo.get_by_employee_date_range(rfid_id, start_date, today)

    # 取得所有記錄
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{guid}", response_model=AttendanceDailyResponse)
async def get_attendance_record(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> AttendanceDaily:
    """取得單一考勤記錄。"""
    repo = AttendanceRepository(db)
    record = await repo.get_by_id(guid)
    if not record:
        raise HTTPException(status_code=404, detail="考勤記錄不存在")
    return record


@router.put("/{guid}", response_model=AttendanceDailyResponse)
async def update_attendance_record(
    guid: str,
    data: AttendanceDailyUpdate,
    db: AsyncSession = Depends(get_db),
) -> AttendanceDaily:
    """更新考勤記錄。"""
    repo = AttendanceRepository(db)
    record = await repo.get_by_id(guid)
    if not record:
        raise HTTPException(status_code=404, detail="考勤記錄不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    return await repo.update(record)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance_record(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除考勤記錄。"""
    repo = AttendanceRepository(db)
    record = await repo.get_by_id(guid)
    if not record:
        raise HTTPException(status_code=404, detail="考勤記錄不存在")

    await repo.delete(record)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
