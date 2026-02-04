"""班表 API 路由。"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schedule import Schedule
from app.repositories.department import DepartmentRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleResponse])
async def get_schedules(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[Schedule]:
    """取得班表列表。"""
    repo = ScheduleRepository(db)
    if include_deleted:
        schedules = await repo.get_all(skip=skip, limit=limit)
    else:
        schedules = await repo.get_all_active(skip=skip, limit=limit)
    return schedules


@router.get("/{guid}", response_model=ScheduleResponse)
async def get_schedule(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """取得單一班表。"""
    repo = ScheduleRepository(db)
    schedule = await repo.get_by_id(guid)
    if not schedule:
        raise HTTPException(status_code=404, detail="班表不存在")
    return schedule


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """新增班表。"""
    schedule_repo = ScheduleRepository(db)
    dept_repo = DepartmentRepository(db)

    # 檢查部門是否存在
    department = await dept_repo.get_by_id(data.Dept_GUID)
    if not department:
        raise HTTPException(status_code=400, detail="部門不存在")

    # 檢查是否已有相同部門和日期的班表
    existing = await schedule_repo.get_by_department_and_day(
        data.Dept_GUID, data.ActiveDay
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="該部門在此日期已有班表設定",
        )

    schedule = Schedule(**data.model_dump())
    return await schedule_repo.create(schedule)


@router.put("/{guid}", response_model=ScheduleResponse)
async def update_schedule(
    guid: str,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """更新班表。"""
    repo = ScheduleRepository(db)
    schedule = await repo.get_by_id(guid)
    if not schedule:
        raise HTTPException(status_code=404, detail="班表不存在")

    if schedule.IsDeleted:
        raise HTTPException(status_code=400, detail="無法更新已刪除的班表")

    update_data = data.model_dump(exclude_unset=True)

    # 如果更新 ActiveDay，檢查是否衝突
    if "ActiveDay" in update_data:
        existing = await repo.get_by_department_and_day(
            schedule.Dept_GUID, update_data["ActiveDay"]
        )
        if existing and existing.GUID != guid:
            raise HTTPException(
                status_code=409,
                detail="該部門在此日期已有班表設定",
            )

    for key, value in update_data.items():
        setattr(schedule, key, value)

    return await repo.update(schedule)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    guid: str,
    deleted_by: str = "SYSTEM",
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除班表（軟刪除）。"""
    repo = ScheduleRepository(db)
    schedule = await repo.get_by_id(guid)
    if not schedule:
        raise HTTPException(status_code=404, detail="班表不存在")

    if schedule.IsDeleted:
        raise HTTPException(status_code=400, detail="班表已被刪除")

    await repo.soft_delete(schedule, deleted_by)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
