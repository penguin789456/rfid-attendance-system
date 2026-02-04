"""彈性設定資料模型。"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlexSetting(Base):
    """彈性設定資料表（軟刪除）。"""

    __tablename__ = "FlexSettings"
    __table_args__ = (
        UniqueConstraint(
            "Dept_GUID",
            name="UQ_FlexSettings_Dept",
            sqlite_where="IsDeleted = 0",
        ),
    )

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    Dept_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("Departments.GUID"), nullable=False
    )
    FlexMinutes: Mapped[int] = mapped_column(Integer, nullable=False)
    IsDeleted: Mapped[bool] = mapped_column(Boolean, default=False)
    DeletedTime: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    DeletedBy: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    department = relationship("Department", back_populates="flex_settings")
    required_configs = relationship("RequiredConfig", back_populates="flex_setting")
