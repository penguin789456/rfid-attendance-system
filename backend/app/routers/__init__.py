"""API 路由。"""

from app.routers.attendance import router as attendance_router
from app.routers.departments import router as departments_router
from app.routers.employees import router as employees_router
from app.routers.flex_settings import router as flex_settings_router
from app.routers.scan import router as scan_router
from app.routers.schedules import router as schedules_router

__all__ = [
    "departments_router",
    "employees_router",
    "schedules_router",
    "flex_settings_router",
    "attendance_router",
    "scan_router",
]
