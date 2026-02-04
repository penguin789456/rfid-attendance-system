"""員工資料存取層。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """員工 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(Employee, db)

    async def get_by_rfid(self, rfid_id: str) -> Employee | None:
        """根據 RFID ID 取得員工。"""
        return await self.get_by_id(rfid_id, "RFID_ID")

    async def get_active_employees(
        self, skip: int = 0, limit: int = 100
    ) -> list[Employee]:
        """取得所有在職員工。"""
        result = await self.db.execute(
            select(Employee)
            .where(Employee.Active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_department(
        self, dept_guid: str, skip: int = 0, limit: int = 100
    ) -> list[Employee]:
        """根據部門取得員工列表。"""
        result = await self.db.execute(
            select(Employee)
            .where(Employee.Dept_GUID == dept_guid)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
