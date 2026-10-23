
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_me_requires_authentication():
    response = client.get("/me")

    assert response.status_code in (401, 403)
