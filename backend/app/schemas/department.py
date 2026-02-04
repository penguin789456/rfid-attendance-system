"""部門 Pydantic schemas。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    """部門基礎 schema。"""

    DeptCode: str
    DeptName: str


class DepartmentCreate(DepartmentBase):
    """建立部門 schema。"""

    pass


class DepartmentUpdate(BaseModel):
    """更新部門 schema。"""

    DeptCode: str | None = None
    DeptName: str | None = None


class DepartmentResponse(DepartmentBase):
    """部門回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    GUID: str
    CreateTime: datetime
    UpdateTime: datetime
