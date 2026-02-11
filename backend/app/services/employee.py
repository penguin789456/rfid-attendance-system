"""員工業務邏輯服務。"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """員工服務，處理員工 CRUD 邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.emp_repo = EmployeeRepository(db)
        self.dept_repo = DepartmentRepository(db)

    async def get_all(
        self, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> list[Employee]:
        """取得員工列表。"""
        if active_only:
            return await self.emp_repo.get_active_employees(skip=skip, limit=limit)
        return await self.emp_repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, guid: str) -> Employee:
        """取得單一員工。"""
        employee = await self.emp_repo.get_by_id(guid)
        if not employee:
            raise HTTPException(status_code=404, detail="員工不存在")
        return employee

    async def create_employee(self, data: EmployeeCreate) -> Employee:
        """新增員工。"""
        # 檢查 RFID ID 是否重複（僅當有提供時）
        if data.RFID_ID:
            existing = await self.emp_repo.get_by_rfid(data.RFID_ID)
            if existing:
                raise HTTPException(status_code=409, detail="RFID ID 已存在")

        # 檢查部門是否存在
        department = await self.dept_repo.get_by_id(data.Dept_GUID)
        if not department:
            raise HTTPException(status_code=400, detail="部門不存在")

        employee = Employee(**data.model_dump())
        return await self.emp_repo.create(employee)

    async def update_employee(self, guid: str, data: EmployeeUpdate) -> Employee:
        """更新員工資料。"""
        employee = await self.emp_repo.get_by_id(guid)
        if not employee:
            raise HTTPException(status_code=404, detail="員工不存在")

        update_data = data.model_dump(exclude_unset=True)

        # 如果要更新 RFID_ID，檢查是否重複
        if "RFID_ID" in update_data and update_data["RFID_ID"]:
            existing = await self.emp_repo.get_by_rfid(update_data["RFID_ID"])
            if existing and existing.GUID != guid:
                raise HTTPException(status_code=409, detail="RFID ID 已存在")

        # 如果要更新部門，檢查部門是否存在
        if "Dept_GUID" in update_data:
            department = await self.dept_repo.get_by_id(update_data["Dept_GUID"])
            if not department:
                raise HTTPException(status_code=400, detail="部門不存在")

        for key, value in update_data.items():
            setattr(employee, key, value)

        return await self.emp_repo.update(employee)

    async def delete_employee(self, guid: str) -> None:
        """刪除員工。"""
        employee = await self.emp_repo.get_by_id(guid)
        if not employee:
            raise HTTPException(status_code=404, detail="員工不存在")

        await self.emp_repo.delete(employee)
