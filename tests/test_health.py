from fastapi.testclient import TestClient

from atlas_api.main import app

client = TestClient(app)


def test_root_identifies_service() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "ATLAS API"


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_endpoint_does_not_fake_a_report() -> None:
    response = client.post(
        "/api/v1/research/reports",
        json={"query": "Analyse ABC Ltd", "market": "IN"},
    )
    assert response.status_code == 501
    assert response.json()["detail"]["code"] == "RESEARCH_ENGINE_NOT_CONFIGURED"
