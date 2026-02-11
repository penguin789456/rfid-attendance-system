"""彈性設定 API 路由。"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.flex_setting import FlexSetting
from app.schemas.flex_setting import (
    FlexSettingCreate,
    FlexSettingResponse,
    FlexSettingUpdate,
)
from app.services.flex_setting import FlexSettingService

router = APIRouter(prefix="/api/flex-settings", tags=["flex-settings"])


@router.get("", response_model=list[FlexSettingResponse])
async def get_flex_settings(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[FlexSetting]:
    """取得彈性設定列表。"""
    service = FlexSettingService(db)
    return await service.get_all(
        skip=skip, limit=limit, include_deleted=include_deleted
    )


@router.get("/{guid}", response_model=FlexSettingResponse)
async def get_flex_setting(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """取得單一彈性設定。"""
    service = FlexSettingService(db)
    return await service.get_by_id(guid)


@router.post(
    "", response_model=FlexSettingResponse, status_code=status.HTTP_201_CREATED
)
async def create_flex_setting(
    data: FlexSettingCreate,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """新增彈性設定。"""
    service = FlexSettingService(db)
    return await service.create_flex_setting(data)


@router.put("/{guid}", response_model=FlexSettingResponse)
async def update_flex_setting(
    guid: str,
    data: FlexSettingUpdate,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """更新彈性設定。"""
    service = FlexSettingService(db)
    return await service.update_flex_setting(guid, data)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flex_setting(
    guid: str,
    deleted_by: str = "SYSTEM",
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除彈性設定（軟刪除）。"""
    service = FlexSettingService(db)
    await service.delete_flex_setting(guid, deleted_by)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
