"""考勤 Pydantic schemas。"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AttendanceDailyBase(BaseModel):
    """考勤基礎 schema。"""

    RFID_ID: str
    WorkDate: date


class AttendanceDailyCreate(AttendanceDailyBase):
    """建立考勤 schema（內部使用）。"""

    RequiredConfigGUID: str | None = None


class AttendanceDailyUpdate(BaseModel):
    """更新考勤 schema。"""

    FirstInTime: datetime | None = None
    LastOutTime: datetime | None = None
    CheckInStatus: int | None = None
    CheckOutStatus: int | None = None
    ExceptionFlags: str | None = None

    @field_validator("CheckInStatus")
    @classmethod
    def validate_check_in_status(cls, v: int | None) -> int | None:
        """驗證 CheckInStatus 必須在 0-2 之間。"""
        if v is not None and v not in (0, 1, 2):
            raise ValueError("CheckInStatus must be 0, 1, or 2")
        return v

    @field_validator("CheckOutStatus")
    @classmethod
    def validate_check_out_status(cls, v: int | None) -> int | None:
        """驗證 CheckOutStatus 必須在 0-2 之間。"""
        if v is not None and v not in (0, 1, 2):
            raise ValueError("CheckOutStatus must be 0, 1, or 2")
        return v


class AttendanceDailyResponse(AttendanceDailyBase):
    """考勤回應 schema。"""

    model_config = ConfigDict(from_attributes=True)

    GUID: str
    RequiredConfigGUID: str | None = None
    FirstInTime: datetime | None = None
    LastOutTime: datetime | None = None
    CheckInStatus: int
    CheckOutStatus: int
    ExceptionFlags: str | None = None
    CreateTime: datetime
    UpdateTime: datetime
