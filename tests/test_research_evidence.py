from atlas_api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def valid_packet() -> dict:
    return {
        "company_identifier": "INE00EXAMPLE",
        "market": "IN",
        "as_of": "2026-11-14T10:00:00+05:30",
        "evidence": [
            {
                "id": "filing-1",
                "source_name": "Example Exchange Filing",
                "source_type": "exchange_disclosure",
                "source_url": "https://example.com/filing/1",
                "published_at": "2026-11-13T09:00:00+05:30",
                "retrieved_at": "2026-11-14T09:00:00+05:30",
                "excerpt": "Example excerpt supplied by the caller.",
            }
        ],
        "claims": [
            {
                "id": "claim-1",
                "statement": "The filing reports a change in revenue.",
                "evidence_ids": ["filing-1"],
                "stance": "supports",
                "as_of": "2026-11-14T10:00:00+05:30",
            }
        ],
    }


def test_valid_evidence_packet_returns_traceability_summary():
    response = client.post("/api/v1/research/evidence-packets/validate", json=valid_packet())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "validated"
    assert body["evidence_count"] == 1
    assert body["claim_count"] == 1
    assert body["stance_counts"]["supports"] == 1
    assert body["unreferenced_evidence_ids"] == []
    assert any("not source authenticity" in item for item in body["limitations"])


def test_packet_rejects_claim_with_unknown_evidence_reference():
    packet = valid_packet()
    packet["claims"][0]["evidence_ids"] = ["missing-source"]

    response = client.post("/api/v1/research/evidence-packets/validate", json=packet)

    assert response.status_code == 422


def test_packet_rejects_duplicate_evidence_ids():
    packet = valid_packet()
    packet["evidence"].append(packet["evidence"][0].copy())

    response = client.post("/api/v1/research/evidence-packets/validate", json=packet)

    assert response.status_code == 422


def test_packet_rejects_timezone_naive_timestamps():
    packet = valid_packet()
    packet["as_of"] = "2026-11-14T10:00:00"

    response = client.post("/api/v1/research/evidence-packets/validate", json=packet)

    assert response.status_code == 422
