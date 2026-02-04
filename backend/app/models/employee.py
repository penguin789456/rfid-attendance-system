"""員工資料模型。"""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    """員工資料表。"""

    __tablename__ = "Employees"

    RFID_ID: Mapped[str] = mapped_column(String, primary_key=True)
    EmpCode: Mapped[str] = mapped_column(String, nullable=False)
    Name: Mapped[str] = mapped_column(String, nullable=False)
    Dept_GUID: Mapped[str] = mapped_column(
        String, ForeignKey("Departments.GUID"), nullable=False
    )
    Active: Mapped[bool] = mapped_column(Boolean, default=True)
    CreateTime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    UpdateTime: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    department = relationship("Department", back_populates="employees")
    scan_events = relationship("ScanEvent", back_populates="employee")
    attendance_records = relationship("AttendanceDaily", back_populates="employee")
