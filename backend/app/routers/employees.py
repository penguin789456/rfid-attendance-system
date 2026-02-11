"""員工 API 路由。"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee import EmployeeService

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[Employee]:
    """取得員工列表。"""
    service = EmployeeService(db)
    return await service.get_all(skip=skip, limit=limit, active_only=active_only)


@router.get("/{guid}", response_model=EmployeeResponse)
async def get_employee(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """取得單一員工。"""
    service = EmployeeService(db)
    return await service.get_by_id(guid)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """新增員工。"""
    service = EmployeeService(db)
    return await service.create_employee(data)


@router.put("/{guid}", response_model=EmployeeResponse)
async def update_employee(
    guid: str,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """更新員工資料。"""
    service = EmployeeService(db)
    return await service.update_employee(guid, data)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除員工。"""
    service = EmployeeService(db)
    await service.delete_employee(guid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
