"""部門資料模型。"""

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    """部門資料表。"""

    __tablename__ = "Departments"

    GUID: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    DeptCode: Mapped[str] = mapped_column(String, nullable=False)
    DeptName: Mapped[str] = mapped_column(String, nullable=False)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    employees = relationship("Employee", back_populates="department")
    schedules = relationship("Schedule", back_populates="department")
    flex_settings = relationship("FlexSetting", back_populates="department")
    required_configs = relationship("RequiredConfig", back_populates="department")
