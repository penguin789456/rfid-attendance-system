"""資料存取層。"""

from app.repositories.attendance import AttendanceRepository
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.flex_setting import FlexSettingRepository
from app.repositories.required_config import RequiredConfigRepository
from app.repositories.scan_event import ScanEventRepository
from app.repositories.schedule import ScheduleRepository

__all__ = [
    "DepartmentRepository",
    "EmployeeRepository",
    "ScheduleRepository",
    "FlexSettingRepository",
    "RequiredConfigRepository",
    "ScanEventRepository",
    "AttendanceRepository",
]
