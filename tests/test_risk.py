import pytest

from atlas_api.domain.risk import (
    annualized_volatility,
    concentration_hhi,
    daily_returns,
    max_drawdown,
    portfolio_return,
)


def test_daily_returns() -> None:
    assert daily_returns([100, 110, 99]) == pytest.approx([0.1, -0.1])


def test_annualized_volatility_is_non_negative() -> None:
    assert annualized_volatility([0.01, -0.01, 0.02]) > 0


def test_max_drawdown() -> None:
    assert max_drawdown([100, 120, 90, 110]) == pytest.approx(-0.25)


def test_hhi() -> None:
    assert concentration_hhi([0.5, 0.5]) == pytest.approx(0.5)


def test_portfolio_return() -> None:
    assert portfolio_return([0.25, 0.75], [0.1, -0.02]) == pytest.approx(0.01)


@pytest.mark.parametrize("prices", [[], [0, 1], [1]])
def test_invalid_price_series(prices: list[float]) -> None:
    with pytest.raises(ValueError):
        daily_returns(prices)


def test_weights_must_sum_to_one() -> None:
    with pytest.raises(ValueError):
        concentration_hhi([0.2, 0.2])
