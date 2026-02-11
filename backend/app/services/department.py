"""部門業務邏輯服務。"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.department import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    """部門服務，處理部門 CRUD 邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.dept_repo = DepartmentRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Department]:
        """取得部門列表。"""
        return await self.dept_repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, guid: str) -> Department:
        """取得單一部門。"""
        department = await self.dept_repo.get_by_id(guid)
        if not department:
            raise HTTPException(status_code=404, detail="部門不存在")
        return department

    async def create_department(self, data: DepartmentCreate) -> Department:
        """新增部門。"""
        # 檢查部門代碼是否重複
        existing = await self.dept_repo.get_by_code(data.DeptCode)
        if existing:
            raise HTTPException(status_code=409, detail="部門代碼已存在")

        department = Department(**data.model_dump())
        return await self.dept_repo.create(department)

    async def update_department(self, guid: str, data: DepartmentUpdate) -> Department:
        """更新部門。"""
        department = await self.dept_repo.get_by_id(guid)
        if not department:
            raise HTTPException(status_code=404, detail="部門不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(department, key, value)

        return await self.dept_repo.update(department)

    async def delete_department(self, guid: str) -> None:
        """刪除部門。"""
        department = await self.dept_repo.get_by_id(guid)
        if not department:
            raise HTTPException(status_code=404, detail="部門不存在")

        await self.dept_repo.delete(department)
