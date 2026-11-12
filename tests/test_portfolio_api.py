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
    assert payload["daily_returns"] == [0.1, -0.1]
    assert payload["max_drawdown"] == -0.1
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
    assert response.json()["weighted_return"] == 0.01
    assert response.json()["concentration_hhi"] == 0.625


def test_allocation_rejects_mismatched_inputs() -> None:
    response = client.post(
        "/api/v1/portfolio/risk/allocation",
        json={"weights": [0.5, 0.5], "asset_returns": [0.1]},
    )
    assert response.status_code == 422
