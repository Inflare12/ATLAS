from datetime import date, timedelta

import pytest

from ml.training.baselines import Observation, train_ridge_baseline, validate_observations


def make_observations(count: int = 160) -> list[Observation]:
    prices = [100.0]
    for index in range(1, count):
        # Deterministic synthetic fixture for software tests only, not market data.
        daily_return = 0.0005 + 0.002 * ((index % 7) - 3)
        prices.append(prices[-1] * (1.0 + daily_return))
    start = date(2020, 1, 1)
    return [Observation(start + timedelta(days=i), price) for i, price in enumerate(prices)]


def test_ridge_baseline_uses_chronological_holdout_and_returns_comparators():
    result = train_ridge_baseline(make_observations())
    assert result["split"]["method"] == "chronological_70_15_15"
    assert result["split"]["training_examples"] > result["split"]["validation_examples"]
    assert set(result["metrics"]) == {
        "test_model",
        "test_zero_return_baseline",
        "test_training_mean_baseline",
    }
    assert len(result["coefficients"]) == 6
    assert len(result["data_fingerprint_sha256"]) == 64


def test_training_rejects_duplicate_or_unordered_dates():
    rows = make_observations()
    invalid = rows.copy()
    invalid[4] = invalid[3]
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_observations(invalid)


def test_training_rejects_too_few_observations():
    with pytest.raises(ValueError, match="at least 40"):
        train_ridge_baseline(make_observations(20))


def test_training_rejects_invalid_close_values():
    rows = make_observations()
    invalid = rows.copy()
    invalid[10] = Observation(invalid[10].day, float("nan"))
    with pytest.raises(ValueError, match="finite and positive"):
        train_ridge_baseline(invalid)
