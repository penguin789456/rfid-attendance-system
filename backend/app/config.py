"""應用程式配置設定。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定。"""

    app_name: str = "RFID Attendance System"
    database_url: str = "sqlite+aiosqlite:///./attendance.db"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
