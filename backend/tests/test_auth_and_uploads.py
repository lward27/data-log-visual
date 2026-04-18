from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.db.session import get_session
from app.main import app


def _build_test_client(tmp_path):
    sqlite_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_register_and_me_flow(tmp_path) -> None:
    upload_root = tmp_path / "uploads"
    settings.upload_root = str(upload_root)

    client = _build_test_client(tmp_path)

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "driver@example.com",
            "password": "supersecret123",
            "display_name": "Driver",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "driver@example.com"

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["display_name"] == "Driver"

    update_response = client.patch(
        "/api/auth/me",
        json={
            "display_name": "Track Driver",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "Track Driver"


def test_upload_flow_creates_visualization_payload(tmp_path) -> None:
    upload_root = tmp_path / "uploads"
    settings.upload_root = str(upload_root)
    client = _build_test_client(tmp_path)

    client.post(
        "/api/auth/register",
        json={
            "email": "upload@example.com",
            "password": "supersecret123",
            "display_name": "Uploader",
        },
    )

    sample_path = Path(__file__).resolve().parents[2] / "data-logs" / "datalog2.csv"
    with sample_path.open("rb") as sample_file:
        upload_response = client.post(
            "/api/uploads",
            files={"file": (sample_path.name, sample_file, "text/csv")},
        )

    assert upload_response.status_code == 201
    payload = upload_response.json()
    assert payload["sample_count"] > 6000
    assert payload["available_metrics"]

    visualization_response = client.get(f"/api/uploads/{payload['id']}/visualization")
    assert visualization_response.status_code == 200
    visualization = visualization_response.json()
    assert len(visualization["time_axis"]) == visualization["sample_count"]
    assert any(metric["key"] == "rpm" for metric in visualization["metrics"])
    assert payload["map_name"]
