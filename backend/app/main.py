from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import create_db_and_tables

app = FastAPI(title=settings.app_name)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def on_startup() -> None:
    Path(settings.upload_root).mkdir(parents=True, exist_ok=True)
    create_db_and_tables()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}


app.include_router(api_router, prefix=settings.api_prefix)
