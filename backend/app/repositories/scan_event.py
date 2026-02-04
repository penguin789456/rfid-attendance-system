"""刷卡事件資料存取層。"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan_event import ScanEvent
from app.repositories.base import BaseRepository


class ScanEventRepository(BaseRepository[ScanEvent]):
    """刷卡事件 Repository。"""

    def __init__(self, db: AsyncSession):
        """初始化 Repository。"""
        super().__init__(ScanEvent, db)

    async def get_by_employee_and_date_range(
        self,
        rfid_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ScanEvent]:
        """取得員工在指定時間範圍內的刷卡記錄。"""
        result = await self.db.execute(
            select(ScanEvent)
            .where(
                and_(
                    ScanEvent.RFID_ID == rfid_id,
                    ScanEvent.EventTime >= start_time,
                    ScanEvent.EventTime <= end_time,
                )
            )
            .order_by(ScanEvent.EventTime)
        )
        return list(result.scalars().all())
