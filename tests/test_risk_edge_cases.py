import math

import pytest

from atlas_api.domain.risk import annualized_volatility, daily_returns, max_drawdown


@pytest.mark.parametrize("prices", [[1, math.nan], [1, math.inf], [1, 0], [1, -1]])
def test_price_calculations_reject_non_finite_or_non_positive_values(
    prices: list[float],
) -> None:
    with pytest.raises(ValueError):
        daily_returns(prices)


@pytest.mark.parametrize("returns", [[0.1, math.nan], [0.1, math.inf], [0.1, -1.1]])
def test_volatility_rejects_invalid_returns(returns: list[float]) -> None:
    with pytest.raises(ValueError):
        annualized_volatility(returns)


def test_flat_prices_have_zero_drawdown() -> None:
    assert max_drawdown([100, 100, 100]) == 0
