"""刷卡業務邏輯服務。"""

from datetime import date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceDaily
from app.models.scan_event import ScanEvent
from app.repositories.attendance import AttendanceRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.flex_setting import FlexSettingRepository
from app.repositories.required_config import RequiredConfigRepository
from app.repositories.scan_event import ScanEventRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.scan import ScanRequest, ScanResponse


class ScanService:
    """刷卡服務，處理打卡邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.schedule_repo = ScheduleRepository(db)
        self.flex_setting_repo = FlexSettingRepository(db)
        self.required_config_repo = RequiredConfigRepository(db)
        self.scan_event_repo = ScanEventRepository(db)
        self.attendance_repo = AttendanceRepository(db)

    async def process_scan(self, request: ScanRequest) -> ScanResponse:
        """處理刷卡事件。"""
        event_time = request.event_time or datetime.utcnow()

        # 1. 驗證員工
        employee = await self.employee_repo.get_by_rfid(request.rfid_id)
        if not employee:
            return ScanResponse(success=False, message="無效的 RFID 卡")

        if not employee.Active:
            return ScanResponse(success=False, message="員工已離職")

        # 2. 取得班表和彈性設定
        weekday = event_time.weekday() + 1  # Python 是 0-6，我們要 1-7
        schedule = await self.schedule_repo.get_schedule_for_date(
            employee.Dept_GUID, weekday
        )
        if not schedule:
            return ScanResponse(
                success=False,
                message="找不到適用的班表",
                employee_name=employee.Name,
            )

        flex_setting = await self.flex_setting_repo.get_by_department(
            employee.Dept_GUID
        )
        flex_minutes = flex_setting.FlexMinutes if flex_setting else 0

        # 3. 使用 DayCutoff 決定 WorkDate
        work_date = self._calculate_work_date(event_time, schedule.DayCutoff)

        # 4. 建立 ScanEvent
        scan_event = ScanEvent(
            RFID_ID=request.rfid_id,
            Device_ID=request.device_id,
            EventTime=event_time,
        )
        await self.scan_event_repo.create(scan_event)

        # 5. Upsert AttendanceDaily
        attendance = await self.attendance_repo.get_by_employee_and_date(
            request.rfid_id, work_date
        )

        if attendance is None:
            # 第一次打卡 - 鎖定規則
            required_config = await self.required_config_repo.get_current_config_for_department(
                employee.Dept_GUID, weekday, work_date
            )

            attendance = AttendanceDaily(
                RFID_ID=request.rfid_id,
                WorkDate=work_date,
                RequiredConfigGUID=required_config.GUID if required_config else None,
                FirstInTime=event_time,
                CheckInStatus=self._calculate_check_in_status(
                    event_time.time(),
                    schedule.CheckInNeedBefore,
                    flex_minutes,
                ),
                CheckOutStatus=2,  # MISSING
            )
            await self.attendance_repo.create(attendance)
            scan_type = "clock_in"
        else:
            # 後續打卡 - 更新 LastOutTime
            attendance.LastOutTime = event_time
            attendance.CheckOutStatus = self._calculate_check_out_status(
                event_time.time(),
                schedule.CheckNeedOutAfter,
            )
            await self.attendance_repo.update(attendance)
            scan_type = "clock_out"

        return ScanResponse(
            success=True,
            message="打卡成功",
            employee_name=employee.Name,
            work_date=work_date.isoformat(),
            scan_type=scan_type,
            check_in_status=attendance.CheckInStatus,
            check_out_status=attendance.CheckOutStatus,
        )

    def _calculate_work_date(self, event_time: datetime, day_cutoff: time) -> date:
        """根據 DayCutoff 計算工作日期。"""
        cutoff_datetime = datetime.combine(event_time.date(), day_cutoff)

        if event_time < cutoff_datetime:
            # 刷卡時間在日切點之前，屬於前一天
            return event_time.date() - timedelta(days=1)
        return event_time.date()

    def _calculate_check_in_status(
        self, scan_time: time, required_in: time, flex_minutes: int
    ) -> int:
        """計算上班打卡狀態。"""
        # 計算彈性結束時間
        required_in_dt = datetime.combine(date.today(), required_in)
        flex_end_dt = required_in_dt + timedelta(minutes=flex_minutes)
        flex_end_time = flex_end_dt.time()

        if scan_time <= required_in:
            return 0  # NORMAL
        elif scan_time <= flex_end_time:
            return 1  # FLEX
        else:
            return 2  # LATE

    def _calculate_check_out_status(
        self, scan_time: time, required_out: time
    ) -> int:
        """計算下班打卡狀態。"""
        if scan_time >= required_out:
            return 0  # NORMAL
        else:
            return 1  # EARLY
