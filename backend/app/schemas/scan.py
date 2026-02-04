"""刷卡 Pydantic schemas。"""

from datetime import datetime

from pydantic import BaseModel


class ScanRequest(BaseModel):
    """刷卡請求 schema。"""

    rfid_id: str
    device_id: str = "DEFAULT"
    event_time: datetime | None = None  # 如果為 None，使用當前時間


class ScanResponse(BaseModel):
    """刷卡回應 schema。"""

    success: bool
    message: str
    employee_name: str | None = None
    work_date: str | None = None
    scan_type: str | None = None  # "clock_in" or "clock_out"
    check_in_status: int | None = None
    check_out_status: int | None = None
