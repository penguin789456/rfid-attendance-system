"""部門資料存取層。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """部門 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(Department, db)

    async def get_by_code(self, dept_code: str) -> Department | None:
        """根據部門代碼取得部門。"""
        result = await self.db.execute(
            select(Department).where(Department.DeptCode == dept_code)
        )
        return result.scalar_one_or_none()
