from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_session
from app.models.entities import DataLogMetric, DataLogUpload, User
from app.schemas.uploads import (
    UploadDetail,
    UploadListItem,
    UploadMetricDetail,
    UploadMetricSummary,
    UploadVisualization,
)
from app.services.datalog_parser import parse_cobb_accessport_csv

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-")
    return cleaned or "datalog.csv"


def _serialize_upload_list_item(upload: DataLogUpload, metric_count: int) -> UploadListItem:
    return UploadListItem(
        id=upload.id,
        original_filename=upload.original_filename,
        source_format=upload.source_format,
        uploaded_at=upload.uploaded_at,
        file_size_bytes=upload.file_size_bytes,
        sample_count=upload.sample_count,
        duration_seconds=upload.duration_seconds,
        metric_count=metric_count,
        device_label=upload.source_metadata.get("device"),
        vehicle_profile=upload.source_metadata.get("vehicle_profile"),
    )


def _serialize_metric_summary(metric: DataLogMetric) -> UploadMetricSummary:
    return UploadMetricSummary(
        key=metric.key,
        display_name=metric.display_name,
        unit=metric.unit,
        sample_count=metric.sample_count,
        min_value=metric.min_value,
        max_value=metric.max_value,
        position=metric.position,
    )


def _load_upload_for_user(session: Session, upload_id: str, user_id: str) -> DataLogUpload:
    upload = session.get(DataLogUpload, upload_id)
    if upload is None or upload.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found.")
    return upload


@router.get("", response_model=list[UploadListItem])
def list_uploads(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[UploadListItem]:
    uploads = session.exec(
        select(DataLogUpload)
        .where(DataLogUpload.user_id == current_user.id)
        .order_by(DataLogUpload.uploaded_at.desc())
    ).all()

    items: list[UploadListItem] = []
    for upload in uploads:
        metric_count = session.exec(
            select(DataLogMetric).where(DataLogMetric.upload_id == upload.id)
        ).all()
        items.append(_serialize_upload_list_item(upload, len(metric_count)))
    return items


@router.post("", response_model=UploadDetail, status_code=status.HTTP_201_CREATED)
async def create_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UploadDetail:
    filename = file.filename or "datalog.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV uploads are supported.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")

    max_upload_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(raw_bytes) > max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_size_mb} MB upload limit.",
        )

    parsed = parse_cobb_accessport_csv(raw_bytes, filename)

    upload_id = str(uuid4())
    safe_name = _sanitize_filename(filename)
    user_dir = Path(settings.upload_root) / current_user.id
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_path = user_dir / f"{upload_id}-{safe_name}"
    stored_path.write_bytes(raw_bytes)

    upload = DataLogUpload(
        id=upload_id,
        user_id=current_user.id,
        source_format=parsed.source_format,
        original_filename=filename,
        stored_path=str(stored_path),
        file_size_bytes=len(raw_bytes),
        sample_count=parsed.sample_count,
        duration_seconds=parsed.duration_seconds,
        time_axis=parsed.time_axis,
        source_metadata=parsed.metadata,
        summary=parsed.summary,
    )
    session.add(upload)

    metrics: list[DataLogMetric] = []
    for metric in parsed.metrics:
        metrics.append(
            DataLogMetric(
                upload_id=upload_id,
                key=metric.key,
                display_name=metric.display_name,
                unit=metric.unit,
                sample_count=metric.sample_count,
                min_value=metric.min_value,
                max_value=metric.max_value,
                position=metric.position,
                values=metric.values,
            )
        )
    for metric in metrics:
        session.add(metric)

    session.commit()
    session.refresh(upload)

    return UploadDetail(
        **_serialize_upload_list_item(upload, len(metrics)).dict(),
        summary=upload.summary,
        source_metadata=upload.source_metadata,
        available_metrics=[_serialize_metric_summary(metric) for metric in metrics],
    )


@router.get("/{upload_id}", response_model=UploadDetail)
def get_upload(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UploadDetail:
    upload = _load_upload_for_user(session, upload_id, current_user.id)
    metrics = session.exec(
        select(DataLogMetric)
        .where(DataLogMetric.upload_id == upload.id)
        .order_by(DataLogMetric.position.asc())
    ).all()

    return UploadDetail(
        **_serialize_upload_list_item(upload, len(metrics)).dict(),
        summary=upload.summary,
        source_metadata=upload.source_metadata,
        available_metrics=[_serialize_metric_summary(metric) for metric in metrics],
    )


@router.get("/{upload_id}/visualization", response_model=UploadVisualization)
def get_upload_visualization(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UploadVisualization:
    upload = _load_upload_for_user(session, upload_id, current_user.id)
    metrics = session.exec(
        select(DataLogMetric)
        .where(DataLogMetric.upload_id == upload.id)
        .order_by(DataLogMetric.position.asc())
    ).all()

    return UploadVisualization(
        **_serialize_upload_list_item(upload, len(metrics)).dict(),
        summary=upload.summary,
        source_metadata=upload.source_metadata,
        available_metrics=[_serialize_metric_summary(metric) for metric in metrics],
        time_axis=upload.time_axis,
        metrics=[
            UploadMetricDetail(
                key=metric.key,
                display_name=metric.display_name,
                unit=metric.unit,
                sample_count=metric.sample_count,
                min_value=metric.min_value,
                max_value=metric.max_value,
                position=metric.position,
                values=metric.values,
            )
            for metric in metrics
        ],
    )


@router.get("/{upload_id}/download")
def download_upload(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FileResponse:
    upload = _load_upload_for_user(session, upload_id, current_user.id)
    path = Path(upload.stored_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file is missing.")
    return FileResponse(path=path, filename=upload.original_filename, media_type="text/csv")
