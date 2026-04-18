from __future__ import annotations

import csv
import io
import math
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricSeries:
    key: str
    display_name: str
    unit: Optional[str]
    values: list[Optional[float]]
    sample_count: int
    min_value: Optional[float]
    max_value: Optional[float]
    position: int


@dataclass
class ParsedDatalog:
    source_format: str
    time_axis: list[float]
    sample_count: int
    duration_seconds: Optional[float]
    metrics: list[MetricSeries]
    metadata: dict[str, object]
    summary: dict[str, object]


def _decode_bytes(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode upload. Expected a valid CSV export.")


def _parse_optional_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def _split_metric_header(header: str) -> tuple[str, Optional[str]]:
    match = re.match(r"^(.*?)(?:\s+\(([^()]*)\))?$", header.strip())
    if not match:
        return header.strip(), None

    display_name = match.group(1).strip()
    unit = match.group(2).strip() if match.group(2) else None
    return display_name, unit


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "metric"


def _parse_ap_info(header: str | None) -> dict[str, object]:
    if not header:
        return {}
    entries = re.findall(r"\[([^\]]+)\]", header)
    metadata = {"raw": header, "entries": entries}
    if entries:
        metadata["device"] = entries[0]
    if len(entries) > 1:
        metadata["vehicle_profile"] = entries[1]
    if len(entries) > 2:
        metadata["map_name"] = entries[2]
    return metadata


def parse_cobb_accessport_csv(raw_bytes: bytes, filename: str) -> ParsedDatalog:
    decoded = _decode_bytes(raw_bytes)
    reader = csv.DictReader(io.StringIO(decoded, newline=""))
    fieldnames = reader.fieldnames or []
    if not fieldnames:
        raise ValueError("The uploaded CSV has no headers.")

    time_header = next((name for name in fieldnames if name.lower().startswith("time")), None)
    if time_header is None:
        raise ValueError("Expected a time column in the uploaded datalog.")

    ap_info_header = next((name for name in fieldnames if name.startswith("AP Info:")), None)
    metric_headers = [name for name in fieldnames if name not in {time_header, ap_info_header}]

    time_axis: list[float] = []
    metric_values: dict[str, list[Optional[float]]] = {header: [] for header in metric_headers}

    for row in reader:
        time_value = _parse_optional_float(row.get(time_header))
        if time_value is None:
            continue
        time_axis.append(time_value)
        for header in metric_headers:
            metric_values[header].append(_parse_optional_float(row.get(header)))

    metrics: list[MetricSeries] = []
    for index, header in enumerate(metric_headers):
        display_name, unit = _split_metric_header(header)
        values = metric_values[header]
        numeric_values = [value for value in values if value is not None]
        metrics.append(
            MetricSeries(
                key=_slugify(display_name),
                display_name=display_name,
                unit=unit,
                values=values,
                sample_count=len(values),
                min_value=min(numeric_values) if numeric_values else None,
                max_value=max(numeric_values) if numeric_values else None,
                position=index,
            )
        )

    sample_count = len(time_axis)
    duration_seconds = time_axis[-1] - time_axis[0] if sample_count > 1 else 0.0 if sample_count == 1 else None
    metadata = _parse_ap_info(ap_info_header)
    summary = {
        "filename": filename,
        "sample_count": sample_count,
        "duration_seconds": duration_seconds,
        "metric_count": len(metrics),
        "available_metric_keys": [metric.key for metric in metrics],
        "highlights": {},
    }

    for key in ("rpm", "boost", "vehicle-speed", "coolant-temp", "dyn-adv-mult", "feedback-knock"):
        metric = next((item for item in metrics if item.key == key), None)
        if metric is None:
            continue
        summary["highlights"][key] = {
            "display_name": metric.display_name,
            "unit": metric.unit,
            "min_value": metric.min_value,
            "max_value": metric.max_value,
        }

    return ParsedDatalog(
        source_format="cobb_accessport",
        time_axis=time_axis,
        sample_count=sample_count,
        duration_seconds=duration_seconds,
        metrics=metrics,
        metadata=metadata,
        summary=summary,
    )
