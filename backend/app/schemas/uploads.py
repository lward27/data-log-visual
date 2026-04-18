from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class UploadMetricSummary(BaseModel):
    key: str
    display_name: str
    unit: Optional[str]
    sample_count: int
    min_value: Optional[float]
    max_value: Optional[float]
    position: int


class UploadMetricDetail(UploadMetricSummary):
    values: list[Optional[float]]


class UploadListItem(BaseModel):
    id: str
    original_filename: str
    source_format: str
    uploaded_at: datetime
    file_size_bytes: int
    sample_count: int
    duration_seconds: Optional[float]
    metric_count: int
    device_label: Optional[str]
    vehicle_profile: Optional[str]


class UploadDetail(UploadListItem):
    summary: dict[str, Any]
    source_metadata: dict[str, Any]
    available_metrics: list[UploadMetricSummary]


class UploadVisualization(UploadDetail):
    time_axis: list[float]
    metrics: list[UploadMetricDetail]
