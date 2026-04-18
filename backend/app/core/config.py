from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, root_validator, validator


class Settings(BaseSettings):
    app_name: str = "Data Log Visual API"
    api_prefix: str = "/api"
    database_url: Optional[str] = None
    pg_host: Optional[str] = None
    pg_port: int = 5432
    pg_database: Optional[str] = None
    pg_user: Optional[str] = None
    pg_password: Optional[str] = None
    upload_root: str = "./uploads"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    session_cookie_name: str = "datalog_session"
    session_ttl_hours: int = 24 * 14
    cookie_secure: bool = False
    max_upload_size_mb: int = 25

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def _split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @root_validator(pre=False)
    def _resolve_database_url(cls, values: dict) -> dict:
        if values.get("database_url"):
            return values

        pg_host = values.get("pg_host")
        pg_database = values.get("pg_database")
        pg_user = values.get("pg_user")
        pg_password = values.get("pg_password")
        pg_port = values.get("pg_port")

        if pg_host and pg_database and pg_user and pg_password:
            values["database_url"] = (
                f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
            )
            return values

        values["database_url"] = "sqlite:///./data-log-visual.db"
        return values


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
