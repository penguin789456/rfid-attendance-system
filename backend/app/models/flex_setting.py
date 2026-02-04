"""彈性設定資料模型。"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlexSetting(Base):
    """彈性設定資料表（軟刪除）。"""

    __tablename__ = "FlexSettings"
    __table_args__ = (
        Index(
            "uix_dept_active",          # 索引名稱
            "Dept_GUID",                # 欄位 (對應你 Schema 中的命名)
            unique=True,                # 強制唯一限制
            sqlite_where=text("IsDeleted = 0") # 關鍵：排除已軟刪除的資料
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
    DeletedTime: Mapped[datetime | None] = mapped_column(nullable=True)
    DeletedBy: Mapped[str | None] = mapped_column(String, nullable=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    department = relationship("Department", back_populates="flex_settings")
    required_configs = relationship("RequiredConfig", back_populates="flex_setting")
