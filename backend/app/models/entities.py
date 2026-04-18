from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    password_hash: str
    display_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    token_hash: str = Field(index=True, sa_column_kwargs={"unique": True})
    expires_at: datetime = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DataLogUpload(SQLModel, table=True):
    __tablename__ = "datalog_uploads"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    source_format: str = Field(default="cobb_accessport", nullable=False)
    original_filename: str
    stored_path: str
    file_size_bytes: int
    sample_count: int
    duration_seconds: Optional[float] = None
    time_axis: list[float] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    source_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)


class DataLogMetric(SQLModel, table=True):
    __tablename__ = "datalog_metrics"
    __table_args__ = (UniqueConstraint("upload_id", "key", name="uq_upload_metric_key"),)

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    upload_id: str = Field(foreign_key="datalog_uploads.id", index=True, nullable=False)
    key: str = Field(index=True)
    display_name: str
    unit: Optional[str] = None
    sample_count: int
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    position: int = 0
    values: list[Optional[float]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
