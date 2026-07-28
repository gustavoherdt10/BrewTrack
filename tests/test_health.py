from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_verificar_api() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "aplicacao": "BrewTrack API",
    }
