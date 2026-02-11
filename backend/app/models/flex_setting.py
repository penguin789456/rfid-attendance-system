"""彈性設定資料模型。"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlexSetting(Base):
    """彈性設定資料表（軟刪除）。"""

    __tablename__ = "FlexSettings"

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    FlexMinutes: Mapped[int] = mapped_column(Integer, nullable=False)
    IsDeleted: Mapped[bool] = mapped_column(Boolean, default=False)
    DeletedTime: Mapped[datetime | None] = mapped_column(nullable=True)
    DeletedBy: Mapped[str | None] = mapped_column(String, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    schedules = relationship("Schedule", back_populates="flex_setting")
    required_configs = relationship("RequiredConfig", back_populates="flex_setting")
