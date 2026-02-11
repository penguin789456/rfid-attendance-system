"""班表業務邏輯服務。"""

from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.required_config import RequiredConfig
from app.models.schedule import Schedule
from app.repositories.department import DepartmentRepository
from app.repositories.flex_setting import FlexSettingRepository
from app.repositories.required_config import RequiredConfigRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """班表服務，處理班表 CRUD 及 RequiredConfig 發布邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.flex_setting_repo = FlexSettingRepository(db)
        self.required_config_repo = RequiredConfigRepository(db)

    async def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Schedule]:
        """取得班表列表。"""
        if include_deleted:
            return await self.schedule_repo.get_all(skip=skip, limit=limit)
        return await self.schedule_repo.get_all_active(skip=skip, limit=limit)

    async def get_by_id(self, guid: str) -> Schedule:
        """取得單一班表。"""
        schedule = await self.schedule_repo.get_by_id(guid)
        if not schedule:
            raise HTTPException(status_code=404, detail="班表不存在")
        return schedule

    async def create_schedule(self, data: ScheduleCreate) -> Schedule:
        """新增班表並發布 RequiredConfig。"""
        # 檢查部門是否存在
        department = await self.dept_repo.get_by_id(data.Dept_GUID)
        if not department:
            raise HTTPException(status_code=400, detail="部門不存在")

        # 檢查 FlexSetting 是否存在（若有指定）
        if data.FlexSetting_GUID:
            flex = await self.flex_setting_repo.get_by_id_active(data.FlexSetting_GUID)
            if not flex:
                raise HTTPException(status_code=400, detail="彈性設定不存在或已刪除")

        # 檢查是否已有相同部門和日期的班表
        existing = await self.schedule_repo.get_by_department_and_day(
            data.Dept_GUID, data.ActiveDay
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="該部門在此日期已有班表設定",
            )

        # 檢查 ActiveDay=8 與 1-7 的衝突
        self._validate_active_day_conflict(
            data.ActiveDay,
            await self.schedule_repo.get_by_department(data.Dept_GUID),
        )

        # 建立班表
        schedule = Schedule(**data.model_dump())
        schedule = await self.schedule_repo.create(schedule)

        # 發布 RequiredConfig 快照
        await self._publish_required_config(schedule)

        return schedule

    async def update_schedule(self, guid: str, data: ScheduleUpdate) -> Schedule:
        """更新班表並重新發布 RequiredConfig。"""
        schedule = await self.schedule_repo.get_by_id(guid)
        if not schedule:
            raise HTTPException(status_code=404, detail="班表不存在")

        if schedule.IsDeleted:
            raise HTTPException(status_code=400, detail="無法更新已刪除的班表")

        update_data = data.model_dump(exclude_unset=True)

        # 檢查 FlexSetting 是否存在（若有更新）
        if "FlexSetting_GUID" in update_data and update_data["FlexSetting_GUID"]:
            flex = await self.flex_setting_repo.get_by_id_active(
                update_data["FlexSetting_GUID"]
            )
            if not flex:
                raise HTTPException(status_code=400, detail="彈性設定不存在或已刪除")

        # 如果更新 ActiveDay，檢查是否衝突
        if "ActiveDay" in update_data:
            new_active_day = update_data["ActiveDay"]
            existing = await self.schedule_repo.get_by_department_and_day(
                schedule.Dept_GUID, new_active_day
            )
            if existing and existing.GUID != guid:
                raise HTTPException(
                    status_code=409,
                    detail="該部門在此日期已有班表設定",
                )

            # 檢查 ActiveDay=8 與 1-7 的衝突
            dept_schedules = await self.schedule_repo.get_by_department(
                schedule.Dept_GUID
            )
            self._validate_active_day_conflict(
                new_active_day,
                [s for s in dept_schedules if s.GUID != guid],
            )

        # 更新欄位
        for key, value in update_data.items():
            setattr(schedule, key, value)
        schedule = await self.schedule_repo.update(schedule)

        # 重新發布 RequiredConfig 快照
        await self._publish_required_config(schedule)

        return schedule

    async def delete_schedule(self, guid: str, deleted_by: str) -> None:
        """軟刪除班表並過期對應的 RequiredConfig。"""
        schedule = await self.schedule_repo.get_by_id(guid)
        if not schedule:
            raise HTTPException(status_code=404, detail="班表不存在")

        if schedule.IsDeleted:
            raise HTTPException(status_code=400, detail="班表已被刪除")

        # 過期對應的 RequiredConfig
        old_config = await self.required_config_repo.get_effective_config(
            schedule.Dept_GUID, schedule.ActiveDay, date.today()
        )
        if old_config:
            await self.required_config_repo.expire_config(old_config, date.today())

        await self.schedule_repo.soft_delete(schedule, deleted_by)

    def _validate_active_day_conflict(
        self, active_day: int, dept_schedules: list[Schedule]
    ) -> None:
        """檢查 ActiveDay=8 與 1-7 的衝突。"""
        if active_day == 8:
            if any(s.ActiveDay != 8 for s in dept_schedules):
                raise HTTPException(
                    status_code=409,
                    detail="該部門已有特定日期班表設定，無法新增全年班表",
                )
        else:
            if any(s.ActiveDay == 8 for s in dept_schedules):
                raise HTTPException(
                    status_code=409,
                    detail="該部門已有全年班表設定，無法新增特定日期班表",
                )

    async def _publish_required_config(self, schedule: Schedule) -> None:
        """建立 RequiredConfig 快照，並過期舊版本。"""
        # 從 Schedule 的 FlexSetting_GUID 取得彈性設定
        flex_minutes = 0
        flex_guid = None
        if schedule.FlexSetting_GUID:
            flex_setting = await self.flex_setting_repo.get_by_id_active(
                schedule.FlexSetting_GUID
            )
            if flex_setting:
                flex_minutes = flex_setting.FlexMinutes
                flex_guid = flex_setting.GUID

        # 過期舊的同部門同 ActiveDay 的 RequiredConfig
        old_config = await self.required_config_repo.get_effective_config(
            schedule.Dept_GUID, schedule.ActiveDay, date.today()
        )
        if old_config:
            await self.required_config_repo.expire_config(old_config, date.today())

        # 建立新的 RequiredConfig 快照
        new_config = RequiredConfig(
            Dept_GUID=schedule.Dept_GUID,
            Schedule_GUID=schedule.GUID,
            FlexSetting_GUID=flex_guid,
            ActiveDay=schedule.ActiveDay,
            RequiredIn=schedule.CheckInNeedBefore,
            RequiredOut=schedule.CheckNeedOutAfter,
            FlexMinutes=flex_minutes,
            DayCutoff=schedule.DayCutoff,
            EffectiveFrom=date.today(),
        )
        await self.required_config_repo.create(new_config)
