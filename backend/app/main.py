"""FastAPI 應用程式入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    attendance_router,
    departments_router,
    employees_router,
    flex_settings_router,
    scan_router,
    schedules_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理。"""
    # 啟動時初始化資料庫
    await init_db()
    yield
    # 關閉時的清理工作（如有需要）


app = FastAPI(
    title=settings.app_name,
    description="企業級 RFID 出勤系統 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(departments_router)
app.include_router(employees_router)
app.include_router(schedules_router)
app.include_router(flex_settings_router)
app.include_router(attendance_router)
app.include_router(scan_router)


@app.get("/")
async def root():
    """根路徑，顯示 API 資訊。"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check():
    """健康檢查端點。"""
    return {"status": "healthy"}
