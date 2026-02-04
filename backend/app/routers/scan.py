"""刷卡 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.scan import ScanRequest, ScanResponse
from app.services.scan import ScanService

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
async def process_scan(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    """處理 RFID 刷卡事件（核心打卡 API）。"""
    service = ScanService(db)
    return await service.process_scan(request)
