"""班表資料模型。"""

import uuid
from datetime import datetime, time

from sqlalchemy import Boolean, ForeignKey, Integer, String, Time, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Schedule(Base):
    """部門班表資料表（軟刪除）。"""

    __tablename__ = "Schedules"
    __table_args__ = (
        Index(
            "UQ_Schedules_Dept_ActiveDay",
            "Dept_GUID",
            "ActiveDay",
            unique=True,
            sqlite_where=text("IsDeleted = 0")
        ),
    )

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    Dept_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("Departments.GUID"), nullable=False
    )
    Name: Mapped[str] = mapped_column(String, nullable=False)
    ActiveDay: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-7, 8=全年
    CheckInNeedBefore: Mapped[time] = mapped_column(Time, nullable=False)
    CheckNeedOutAfter: Mapped[time] = mapped_column(Time, nullable=False)
    DayCutoff: Mapped[time] = mapped_column(Time, nullable=False)
    IsDeleted: Mapped[bool] = mapped_column(Boolean, default=False)
    DeletedTime: Mapped[datetime | None] = mapped_column(nullable=True)
    DeletedBy: Mapped[str | None] = mapped_column(String, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    department = relationship("Department", back_populates="schedules")
    required_configs = relationship("RequiredConfig", back_populates="schedule")
