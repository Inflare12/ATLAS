import pytest

from atlas_api.domain.risk import annualized_downside_deviation, historical_var_cvar


def test_historical_var_and_cvar_use_lower_tail() -> None:
    result = historical_var_cvar(
        [-0.10, -0.05, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
        confidence_level=0.8,
    )
    assert result["var_loss_fraction"] == pytest.approx(0.05)
    assert result["cvar_loss_fraction"] == pytest.approx(0.075)
    assert result["tail_observations"] == 2


def test_historical_var_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        historical_var_cvar([-0.1, 0.1], confidence_level=1.0)


def test_downside_deviation_is_zero_when_no_shortfalls() -> None:
    assert annualized_downside_deviation([0.01, 0.02, 0.03]) == 0.0


def test_downside_deviation_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError):
        annualized_downside_deviation([0.01, float("inf")])
