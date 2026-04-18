from pathlib import Path

from app.services.datalog_parser import parse_cobb_accessport_csv


def test_parser_extracts_metrics_and_metadata() -> None:
    sample_path = Path(__file__).resolve().parents[2] / "data-logs" / "datalog1.csv"
    parsed = parse_cobb_accessport_csv(sample_path.read_bytes(), sample_path.name)

    assert parsed.source_format == "cobb_accessport"
    assert parsed.sample_count > 4000
    assert parsed.duration_seconds is not None
    assert parsed.duration_seconds > 0
    assert any(metric.key == "boost" for metric in parsed.metrics)
    assert parsed.metadata["device"]
    assert parsed.summary["metric_count"] >= 30
