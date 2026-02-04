"""員工 Pydantic schemas。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    """員工基礎 schema。"""

    RFID_ID: str
    EmpCode: str
    Name: str
    Dept_GUID: str
    Active: bool = True


class EmployeeCreate(EmployeeBase):
    """建立員工 schema。"""

    pass


class EmployeeUpdate(BaseModel):
    """更新員工 schema。"""

    EmpCode: str | None = None
    Name: str | None = None
    Dept_GUID: str | None = None
    Active: bool | None = None


class EmployeeResponse(EmployeeBase):
    """員工回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    CreateTime: datetime
    UpdateTime: datetime
