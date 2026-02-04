"""員工 API 路由。"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.employee import Employee
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[Employee]:
    """取得員工列表。"""
    repo = EmployeeRepository(db)
    if active_only:
        employees = await repo.get_active_employees(skip=skip, limit=limit)
    else:
        employees = await repo.get_all(skip=skip, limit=limit)
    return employees


@router.get("/{rfid_id}", response_model=EmployeeResponse)
async def get_employee(
    rfid_id: str,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """取得單一員工。"""
    repo = EmployeeRepository(db)
    employee = await repo.get_by_rfid(rfid_id)
    if not employee:
        raise HTTPException(status_code=404, detail="員工不存在")
    return employee


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """新增員工。"""
    emp_repo = EmployeeRepository(db)
    dept_repo = DepartmentRepository(db)

    # 檢查 RFID ID 是否重複
    existing = await emp_repo.get_by_rfid(data.RFID_ID)
    if existing:
        raise HTTPException(status_code=409, detail="RFID ID 已存在")

    # 檢查部門是否存在
    department = await dept_repo.get_by_id(data.Dept_GUID)
    if not department:
        raise HTTPException(status_code=400, detail="部門不存在")

    employee = Employee(**data.model_dump())
    return await emp_repo.create(employee)


@router.put("/{rfid_id}", response_model=EmployeeResponse)
async def update_employee(
    rfid_id: str,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    """更新員工資料。"""
    emp_repo = EmployeeRepository(db)
    dept_repo = DepartmentRepository(db)

    employee = await emp_repo.get_by_rfid(rfid_id)
    if not employee:
        raise HTTPException(status_code=404, detail="員工不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 如果要更新部門，檢查部門是否存在
    if "Dept_GUID" in update_data:
        department = await dept_repo.get_by_id(update_data["Dept_GUID"])
        if not department:
            raise HTTPException(status_code=400, detail="部門不存在")

    for key, value in update_data.items():
        setattr(employee, key, value)

    return await emp_repo.update(employee)


@router.delete("/{rfid_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    rfid_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """刪除員工。"""
    repo = EmployeeRepository(db)
    employee = await repo.get_by_rfid(rfid_id)
    if not employee:
        raise HTTPException(status_code=404, detail="員工不存在")

    await repo.delete(employee)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
