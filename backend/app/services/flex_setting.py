"""彈性設定業務邏輯服務。"""

from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flex_setting import FlexSetting
from app.models.required_config import RequiredConfig
from app.repositories.department import DepartmentRepository
from app.repositories.flex_setting import FlexSettingRepository
from app.repositories.required_config import RequiredConfigRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.flex_setting import FlexSettingCreate, FlexSettingUpdate


class FlexSettingService:
    """彈性設定服務，處理彈性設定 CRUD 及 RequiredConfig 發布邏輯。"""

    def __init__(self, db: AsyncSession):
        """初始化服務。"""
        self.db = db
        self.flex_setting_repo = FlexSettingRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.schedule_repo = ScheduleRepository(db)
        self.required_config_repo = RequiredConfigRepository(db)

    async def get_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[FlexSetting]:
        """取得彈性設定列表。"""
        if include_deleted:
            return await self.flex_setting_repo.get_all(skip=skip, limit=limit)
        return await self.flex_setting_repo.get_all_active(skip=skip, limit=limit)

    async def get_by_id(self, guid: str) -> FlexSetting:
        """取得單一彈性設定。"""
        flex_setting = await self.flex_setting_repo.get_by_id(guid)
        if not flex_setting:
            raise HTTPException(status_code=404, detail="彈性設定不存在")
        return flex_setting

    async def create_flex_setting(self, data: FlexSettingCreate) -> FlexSetting:
        """新增彈性設定並為該部門所有班表發布 RequiredConfig。"""
        # 檢查部門是否存在
        department = await self.dept_repo.get_by_id(data.Dept_GUID)
        if not department:
            raise HTTPException(status_code=400, detail="部門不存在")

        # 檢查該部門是否已有彈性設定
        existing = await self.flex_setting_repo.get_by_department(data.Dept_GUID)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="該部門已有彈性設定",
            )

        # 建立彈性設定
        flex_setting = FlexSetting(**data.model_dump())
        flex_setting = await self.flex_setting_repo.create(flex_setting)

        # 為該部門所有有效班表重新發布 RequiredConfig
        await self._republish_all_configs(data.Dept_GUID, flex_setting)

        return flex_setting

    async def update_flex_setting(
        self, guid: str, data: FlexSettingUpdate
    ) -> FlexSetting:
        """更新彈性設定並重新發布 RequiredConfig。"""
        flex_setting = await self.flex_setting_repo.get_by_id(guid)
        if not flex_setting:
            raise HTTPException(status_code=404, detail="彈性設定不存在")

        if flex_setting.IsDeleted:
            raise HTTPException(status_code=400, detail="無法更新已刪除的彈性設定")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(flex_setting, key, value)

        flex_setting = await self.flex_setting_repo.update(flex_setting)

        # 為該部門所有有效班表重新發布 RequiredConfig
        await self._republish_all_configs(flex_setting.Dept_GUID, flex_setting)

        return flex_setting

    async def delete_flex_setting(self, guid: str, deleted_by: str) -> None:
        """軟刪除彈性設定並過期對應的 RequiredConfig。"""
        flex_setting = await self.flex_setting_repo.get_by_id(guid)
        if not flex_setting:
            raise HTTPException(status_code=404, detail="彈性設定不存在")

        if flex_setting.IsDeleted:
            raise HTTPException(status_code=400, detail="彈性設定已被刪除")

        # 為該部門所有有效班表重新發布 RequiredConfig（FlexMinutes 歸零）
        dept_schedules = await self.schedule_repo.get_by_department(
            flex_setting.Dept_GUID
        )
        for schedule in dept_schedules:
            old_config = await self.required_config_repo.get_effective_config(
                flex_setting.Dept_GUID, schedule.ActiveDay, date.today()
            )
            if old_config:
                await self.required_config_repo.expire_config(
                    old_config, date.today()
                )

            # 建立新的 RequiredConfig（FlexMinutes=0）
            new_config = RequiredConfig(
                Dept_GUID=flex_setting.Dept_GUID,
                Schedule_GUID=schedule.GUID,
                FlexSetting_GUID=None,
                ActiveDay=schedule.ActiveDay,
                RequiredIn=schedule.CheckInNeedBefore,
                RequiredOut=schedule.CheckNeedOutAfter,
                FlexMinutes=0,
                DayCutoff=schedule.DayCutoff,
                EffectiveFrom=date.today(),
            )
            await self.required_config_repo.create(new_config)

        await self.flex_setting_repo.soft_delete(flex_setting, deleted_by)

    async def _republish_all_configs(
        self, dept_guid: str, flex_setting: FlexSetting
    ) -> None:
        """為該部門所有有效班表重新發布 RequiredConfig。"""
        dept_schedules = await self.schedule_repo.get_by_department(dept_guid)

        for schedule in dept_schedules:
            # 過期舊的 RequiredConfig
            old_config = await self.required_config_repo.get_effective_config(
                dept_guid, schedule.ActiveDay, date.today()
            )
            if old_config:
                await self.required_config_repo.expire_config(
                    old_config, date.today()
                )

            # 建立新的 RequiredConfig 快照
            new_config = RequiredConfig(
                Dept_GUID=dept_guid,
                Schedule_GUID=schedule.GUID,
                FlexSetting_GUID=flex_setting.GUID,
                ActiveDay=schedule.ActiveDay,
                RequiredIn=schedule.CheckInNeedBefore,
                RequiredOut=schedule.CheckNeedOutAfter,
                FlexMinutes=flex_setting.FlexMinutes,
                DayCutoff=schedule.DayCutoff,
                EffectiveFrom=date.today(),
            )
            await self.required_config_repo.create(new_config)
