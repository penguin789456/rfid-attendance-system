"""班表 API 路由。"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services.schedule import ScheduleService

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleResponse])
async def get_schedules(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[Schedule]:
    """取得班表列表。"""
    service = ScheduleService(db)
    return await service.get_all(
        skip=skip, limit=limit, include_deleted=include_deleted
    )


@router.get("/{guid}", response_model=ScheduleResponse)
async def get_schedule(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """取得單一班表。"""
    service = ScheduleService(db)
    return await service.get_by_id(guid)


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """新增班表。"""
    service = ScheduleService(db)
    return await service.create_schedule(data)


@router.put("/{guid}", response_model=ScheduleResponse)
async def update_schedule(
    guid: str,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
) -> Schedule:
    """更新班表。"""
    service = ScheduleService(db)
    return await service.update_schedule(guid, data)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    guid: str,
    deleted_by: str = "SYSTEM",
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除班表（軟刪除）。"""
    service = ScheduleService(db)
    await service.delete_schedule(guid, deleted_by)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
