"""彈性設定業務邏輯服務。"""

from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flex_setting import FlexSetting
from app.models.required_config import RequiredConfig
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
        """新增彈性設定。"""
        flex_setting = FlexSetting(**data.model_dump())
        flex_setting = await self.flex_setting_repo.create(flex_setting)
        return flex_setting

    async def update_flex_setting(
        self, guid: str, data: FlexSettingUpdate
    ) -> FlexSetting:
        """更新彈性設定並重新發布引用此設定的 RequiredConfig。"""
        flex_setting = await self.flex_setting_repo.get_by_id(guid)
        if not flex_setting:
            raise HTTPException(status_code=404, detail="彈性設定不存在")

        if flex_setting.IsDeleted:
            raise HTTPException(status_code=400, detail="無法更新已刪除的彈性設定")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(flex_setting, key, value)

        flex_setting = await self.flex_setting_repo.update(flex_setting)

        # 重新發布引用此 FlexSetting 的所有有效班表的 RequiredConfig
        await self._republish_all_configs(flex_setting)

        return flex_setting

    async def delete_flex_setting(self, guid: str, deleted_by: str) -> None:
        """軟刪除彈性設定並過期對應的 RequiredConfig。"""
        flex_setting = await self.flex_setting_repo.get_by_id(guid)
        if not flex_setting:
            raise HTTPException(status_code=404, detail="彈性設定不存在")

        if flex_setting.IsDeleted:
            raise HTTPException(status_code=400, detail="彈性設定已被刪除")

        # 找出引用此 FlexSetting 的所有有效班表
        # 重新發布 RequiredConfig（FlexMinutes=0）
        schedules = await self.schedule_repo.get_by_flex_setting(guid)
        for schedule in schedules:
            old_config = await self.required_config_repo.get_effective_config(
                schedule.Dept_GUID, schedule.ActiveDay, date.today()
            )
            if old_config:
                await self.required_config_repo.expire_config(old_config, date.today())

            # 建立新的 RequiredConfig（FlexMinutes=0）
            new_config = RequiredConfig(
                Dept_GUID=schedule.Dept_GUID,
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

            # 清除班表上的 FlexSetting_GUID 參照
            schedule.FlexSetting_GUID = None
            await self.schedule_repo.update(schedule)

        await self.flex_setting_repo.soft_delete(flex_setting, deleted_by)

    async def _republish_all_configs(self, flex_setting: FlexSetting) -> None:
        """為引用此 FlexSetting 的所有有效班表重新發布 RequiredConfig。"""
        schedules = await self.schedule_repo.get_by_flex_setting(flex_setting.GUID)

        for schedule in schedules:
            # 過期舊的 RequiredConfig
            old_config = await self.required_config_repo.get_effective_config(
                schedule.Dept_GUID, schedule.ActiveDay, date.today()
            )
            if old_config:
                await self.required_config_repo.expire_config(old_config, date.today())

            # 建立新的 RequiredConfig 快照
            new_config = RequiredConfig(
                Dept_GUID=schedule.Dept_GUID,
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
