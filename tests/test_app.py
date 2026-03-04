from fastapi.testclient import TestClient

from app.main import app


def test_app_starts_and_returns_404_for_root() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 404
