"""部門 API 路由。"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department import DepartmentService

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
async def get_departments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[Department]:
    """取得部門列表。"""
    service = DepartmentService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{guid}", response_model=DepartmentResponse)
async def get_department(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """取得單一部門。"""
    service = DepartmentService(db)
    return await service.get_by_id(guid)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """新增部門。"""
    service = DepartmentService(db)
    return await service.create_department(data)


@router.put("/{guid}", response_model=DepartmentResponse)
async def update_department(
    guid: str,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """更新部門。"""
    service = DepartmentService(db)
    return await service.update_department(guid, data)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除部門。"""
    service = DepartmentService(db)
    await service.delete_department(guid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
