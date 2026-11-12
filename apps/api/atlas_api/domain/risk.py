"""Transparent portfolio calculations over validated price/weight inputs."""
from math import sqrt
from statistics import stdev
from typing import Sequence


def _finite_positive(values: Sequence[float], name: str) -> list[float]:
    result = [float(value) for value in values]
    if not result or any(not (value > 0 and value < float("inf")) for value in result):
        raise ValueError(f"{name} must contain finite positive values")
    return result


def daily_returns(prices: Sequence[float]) -> list[float]:
    """Simple close-to-close returns. Prices must be chronological and positive."""
    series = _finite_positive(prices, "prices")
    if len(series) < 2:
        raise ValueError("at least two prices are required")
    return [(current / previous) - 1.0 for previous, current in zip(series, series[1:])]


def annualized_volatility(returns: Sequence[float], periods_per_year: int = 252) -> float:
    values = [float(value) for value in returns]
    if len(values) < 2:
        raise ValueError("at least two returns are required")
    if periods_per_year <= 0 or any(not (-1 < x < float("inf")) for x in values):
        raise ValueError("returns or periods_per_year are invalid")
    return stdev(values) * sqrt(periods_per_year)


def max_drawdown(prices: Sequence[float]) -> float:
    """Return the worst peak-to-trough drawdown as a negative fraction."""
    series = _finite_positive(prices, "prices")
    peak = series[0]
    worst = 0.0
    for price in series:
        peak = max(peak, price)
        worst = min(worst, price / peak - 1.0)
    return worst


def concentration_hhi(weights: Sequence[float]) -> float:
    """Herfindahl index for long-only portfolio weights expressed as fractions."""
    values = [float(value) for value in weights]
    if not values or any(value < 0 or value >= float("inf") for value in values):
        raise ValueError("weights must be finite and non-negative")
    if abs(sum(values) - 1.0) > 1e-6:
        raise ValueError("weights must sum to 1")
    return sum(value * value for value in values)


def portfolio_return(weights: Sequence[float], asset_returns: Sequence[float]) -> float:
    """Single-period weighted return; inputs must align and weights sum to one."""
    w = [float(value) for value in weights]
    r = [float(value) for value in asset_returns]
    if not w or len(w) != len(r):
        raise ValueError("weights and asset_returns must be non-empty and equal length")
    if any(x < 0 or x >= float("inf") for x in w) or any(
        not (-1 <= x < float("inf")) for x in r
    ):
        raise ValueError("inputs must be finite; weights non-negative and returns >= -100%")
    if abs(sum(w) - 1.0) > 1e-6:
        raise ValueError("weights must sum to 1")
    return sum(weight * asset_return for weight, asset_return in zip(w, r))
