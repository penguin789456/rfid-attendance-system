"""部門 API 路由。"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.department import Department
from app.repositories.department import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
async def get_departments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[Department]:
    """取得部門列表。"""
    repo = DepartmentRepository(db)
    departments = await repo.get_all(skip=skip, limit=limit)
    return departments


@router.get("/{guid}", response_model=DepartmentResponse)
async def get_department(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """取得單一部門。"""
    repo = DepartmentRepository(db)
    department = await repo.get_by_id(guid)
    if not department:
        raise HTTPException(status_code=404, detail="部門不存在")
    return department


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """新增部門。"""
    repo = DepartmentRepository(db)

    # 檢查部門代碼是否重複
    existing = await repo.get_by_code(data.DeptCode)
    if existing:
        raise HTTPException(status_code=409, detail="部門代碼已存在")

    department = Department(**data.model_dump())
    return await repo.create(department)


@router.put("/{guid}", response_model=DepartmentResponse)
async def update_department(
    guid: str,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Department:
    """更新部門。"""
    repo = DepartmentRepository(db)
    department = await repo.get_by_id(guid)
    if not department:
        raise HTTPException(status_code=404, detail="部門不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(department, key, value)

    return await repo.update(department)


@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    guid: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除部門。"""
    repo = DepartmentRepository(db)
    department = await repo.get_by_id(guid)
    if not department:
        raise HTTPException(status_code=404, detail="部門不存在")

    await repo.delete(department)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
