"""班表 Pydantic schemas。"""

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, field_validator


class ScheduleBase(BaseModel):
    """班表基礎 schema。"""

    Dept_GUID: str
    Name: str
    ActiveDay: int  # 1-7 (Mon-Sun), 8=全年
    CheckInNeedBefore: time
    CheckNeedOutAfter: time
    DayCutoff: time

    @field_validator("ActiveDay")
    @classmethod
    def validate_active_day(cls, v: int) -> int:
        """驗證 ActiveDay 必須在 1-8 之間。"""
        if v < 1 or v > 8:
            raise ValueError("ActiveDay must be between 1 and 8")
        return v


class ScheduleCreate(ScheduleBase):
    """建立班表 schema。"""

    pass


class ScheduleUpdate(BaseModel):
    """更新班表 schema。"""

    Name: str | None = None
    ActiveDay: int | None = None
    CheckInNeedBefore: time | None = None
    CheckNeedOutAfter: time | None = None
    DayCutoff: time | None = None

    @field_validator("ActiveDay")
    @classmethod
    def validate_active_day(cls, v: int | None) -> int | None:
        """驗證 ActiveDay 必須在 1-8 之間。"""
        if v is not None and (v < 1 or v > 8):
            raise ValueError("ActiveDay must be between 1 and 8")
        return v


class ScheduleResponse(ScheduleBase):
    """班表回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    GUID: str
    IsDeleted: bool
    DeletedTime: datetime | None = None
    DeletedBy: str | None = None
    CreateTime: datetime
    UpdateTime: datetime
