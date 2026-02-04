"""規則配置快照資料模型。"""

import uuid
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RequiredConfig(Base):
    """規則版本快照資料表（不可變）。"""

    __tablename__ = "RequiredConfigs"

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    Dept_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("Departments.GUID"), nullable=False
    )
    Schedule_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("Schedules.GUID"), nullable=False
    )
    FlexSetting_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("FlexSettings.GUID"), nullable=False
    )
    ActiveDay: Mapped[int] = mapped_column(Integer, nullable=False)
    RequiredIn: Mapped[time] = mapped_column(Time, nullable=False)
    RequiredOut: Mapped[time] = mapped_column(Time, nullable=False)
    FlexMinutes: Mapped[int] = mapped_column(Integer, nullable=False)
    DayCutoff: Mapped[time] = mapped_column(Time, nullable=False)
    EffectiveFrom: Mapped[date] = mapped_column(Date, nullable=False)
    EffectiveTo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="required_configs")
    schedule = relationship("Schedule", back_populates="required_configs")
    flex_setting = relationship("FlexSetting", back_populates="required_configs")
    attendance_records = relationship(
        "AttendanceDaily", back_populates="required_config"
    )
