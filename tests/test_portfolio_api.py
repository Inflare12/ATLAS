import pytest
from fastapi.testclient import TestClient

from atlas_api.main import app

client = TestClient(app)


def test_price_series_risk_endpoint() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/price-series",
        json={"prices": [100, 110, 99]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["daily_returns"] == pytest.approx([0.1, -0.1])
    assert payload["max_drawdown"] == pytest.approx(-0.1)
    assert payload["data_source"] == "caller_supplied"
    assert "not forecasts" in payload["limitations"][0]


def test_price_series_rejects_invalid_prices() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/price-series",
        json={"prices": [100, 0]},
    )
    assert response.status_code == 422


def test_allocation_endpoint() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/allocation",
        json={"weights": [0.25, 0.75], "asset_returns": [0.1, -0.02]},
    )
    assert response.status_code == 200
    assert response.json()["weighted_return"] == pytest.approx(0.01)
    assert response.json()["concentration_hhi"] == 0.625


def test_allocation_rejects_mismatched_inputs() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/allocation",
        json={"weights": [0.5, 0.5], "asset_returns": [0.1]},
    )
    assert response.status_code == 422


def test_returns_distribution_endpoint() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/returns-distribution",
        json={
            "returns": [-0.10, -0.05, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
            "confidence_level": 0.8,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["var_loss_fraction"] == pytest.approx(0.05)
    assert payload["cvar_loss_fraction"] == pytest.approx(0.075)
    assert payload["tail_observations"] == 2
    assert payload["methodology"] == "nearest_rank_empirical_lower_tail"


def test_returns_distribution_rejects_invalid_confidence() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/returns-distribution",
        json={"returns": [-0.1, 0.1], "confidence_level": 1.0},
    )
    assert response.status_code == 422
