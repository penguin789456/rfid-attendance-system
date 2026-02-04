"""彈性設定 Pydantic schemas。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class FlexSettingBase(BaseModel):
    """彈性設定基礎 schema。"""

    Dept_GUID: str
    FlexMinutes: int

    @field_validator("FlexMinutes")
    @classmethod
    def validate_flex_minutes(cls, v: int) -> int:
        """驗證 FlexMinutes 必須為非負數。"""
        if v < 0:
            raise ValueError("FlexMinutes must be non-negative")
        return v


class FlexSettingCreate(FlexSettingBase):
    """建立彈性設定 schema。"""

    pass


class FlexSettingUpdate(BaseModel):
    """更新彈性設定 schema。"""

    FlexMinutes: int | None = None

    @field_validator("FlexMinutes")
    @classmethod
    def validate_flex_minutes(cls, v: int | None) -> int | None:
        """驗證 FlexMinutes 必須為非負數。"""
        if v is not None and v < 0:
            raise ValueError("FlexMinutes must be non-negative")
        return v


class FlexSettingResponse(FlexSettingBase):
    """彈性設定回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    GUID: str
    IsDeleted: bool
    DeletedTime: datetime | None = None
    DeletedBy: str | None = None
    CreateTime: datetime
    UpdateTime: datetime
