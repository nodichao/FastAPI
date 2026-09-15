
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_chat():
    response = client.post(
        "/chat",
        json={
            "message": "Bonjour"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
