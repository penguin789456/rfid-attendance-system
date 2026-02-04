"""彈性設定 API 路由。"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.flex_setting import FlexSetting
from app.repositories.department import DepartmentRepository
from app.repositories.flex_setting import FlexSettingRepository
from app.schemas.flex_setting import (
    FlexSettingCreate,
    FlexSettingResponse,
    FlexSettingUpdate,
)

router = APIRouter(prefix="/api/flex-settings", tags=["flex-settings"])


@router.get("", response_model=list[FlexSettingResponse])
async def get_flex_settings(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[FlexSetting]:
    """取得彈性設定列表。"""
    repo = FlexSettingRepository(db)
    if include_deleted:
        flex_settings = await repo.get_all(skip=skip, limit=limit)
    else:
        flex_settings = await repo.get_all_active(skip=skip, limit=limit)
    return flex_settings


@router.get("/{guid}", response_model=FlexSettingResponse)
async def get_flex_setting(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """取得單一彈性設定。"""
    repo = FlexSettingRepository(db)
    flex_setting = await repo.get_by_id(guid)
    if not flex_setting:
        raise HTTPException(status_code=404, detail="彈性設定不存在")
    return flex_setting


@router.post(
    "", response_model=FlexSettingResponse, status_code=status.HTTP_201_CREATED
)
async def create_flex_setting(
    data: FlexSettingCreate,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """新增彈性設定。"""
    flex_repo = FlexSettingRepository(db)
    dept_repo = DepartmentRepository(db)

    # 檢查部門是否存在
    department = await dept_repo.get_by_id(data.Dept_GUID)
    if not department:
        raise HTTPException(status_code=400, detail="部門不存在")

    # 檢查該部門是否已有彈性設定
    existing = await flex_repo.get_by_department(data.Dept_GUID)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="該部門已有彈性設定",
        )

    flex_setting = FlexSetting(**data.model_dump())
    return await flex_repo.create(flex_setting)


@router.put("/{guid}", response_model=FlexSettingResponse)
async def update_flex_setting(
    guid: str,
    data: FlexSettingUpdate,
    db: AsyncSession = Depends(get_db),
) -> FlexSetting:
    """更新彈性設定。"""
    repo = FlexSettingRepository(db)
    flex_setting = await repo.get_by_id(guid)
    if not flex_setting:
        raise HTTPException(status_code=404, detail="彈性設定不存在")

    if flex_setting.IsDeleted:
        raise HTTPException(status_code=400, detail="無法更新已刪除的彈性設定")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(flex_setting, key, value)

    return await repo.update(flex_setting)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flex_setting(
    guid: str,
    deleted_by: str = "SYSTEM",
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除彈性設定（軟刪除）。"""
    repo = FlexSettingRepository(db)
    flex_setting = await repo.get_by_id(guid)
    if not flex_setting:
        raise HTTPException(status_code=404, detail="彈性設定不存在")

    if flex_setting.IsDeleted:
        raise HTTPException(status_code=400, detail="彈性設定已被刪除")

    await repo.soft_delete(flex_setting, deleted_by)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
