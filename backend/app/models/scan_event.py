"""刷卡事件資料模型。"""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScanEvent(Base):
    """原始刷卡事件資料表。"""

    __tablename__ = "ScanEvents"

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    RFID_ID: Mapped[str] = mapped_column(
        String, ForeignKey("Employees.RFID_ID"), nullable=False
    )
    Device_ID: Mapped[str] = mapped_column(String, nullable=False)
    EventTime: Mapped[datetime] = mapped_column(nullable=False)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="scan_events")
