"""每日考勤結果資料模型。"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttendanceDaily(Base):
    """每日考勤結果資料表。"""

    __tablename__ = "AttendanceDaily"

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    RFID_ID: Mapped[str] = mapped_column(
        String, ForeignKey("Employees.RFID_ID"), nullable=False
    )
    WorkDate: Mapped[date] = mapped_column(Date, nullable=False)
    RequiredConfigGUID: Mapped[str | None] = mapped_column(
        String, ForeignKey("RequiredConfigs.GUID"), nullable=True
    )
    FirstInTime: Mapped[datetime | None] = mapped_column(nullable=True)
    LastOutTime: Mapped[datetime | None] = mapped_column(nullable=True)
    CheckInStatus: Mapped[int] = mapped_column(
        Integer, default=0
    )  # 0=NORMAL, 1=FLEX, 2=LATE
    CheckOutStatus: Mapped[int] = mapped_column(
        Integer, default=2
    )  # 0=NORMAL, 1=EARLY, 2=MISSING
    ExceptionFlags: Mapped[str | None] = mapped_column(String, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")
    required_config = relationship(
        "RequiredConfig", back_populates="attendance_records"
    )
