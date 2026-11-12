"""Transparent portfolio calculations over validated price/weight inputs."""
from math import ceil, isfinite, sqrt
from statistics import stdev
from typing import Sequence


def _finite_positive(values: Sequence[float], name: str) -> list[float]:
    result = [float(value) for value in values]
    if not result or any(not isfinite(value) or value <= 0 for value in result):
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
    if periods_per_year <= 0 or any(not (isfinite(x) and x >= -1) for x in values):
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
    if not values or any(not isfinite(value) or value < 0 for value in values):
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
    if any(not isfinite(x) or x < 0 for x in w) or any(
        not isfinite(x) or x < -1 for x in r
    ):
        raise ValueError("inputs must be finite; weights non-negative and returns >= -100%")
    if abs(sum(w) - 1.0) > 1e-6:
        raise ValueError("weights must sum to 1")
    return sum(weight * asset_return for weight, asset_return in zip(w, r))


def historical_var_cvar(
    returns: Sequence[float], confidence_level: float = 0.95
) -> dict[str, float | int]:
    """Empirical historical VaR/CVaR, expressed as loss fractions.

    Uses a nearest-rank empirical lower tail. The number of tail observations is
    ceil((1 - confidence_level) * n), with at least one observation.
    """
    values = [float(value) for value in returns]
    if len(values) < 2 or any(not isfinite(value) or value < -1 for value in values):
        raise ValueError("returns must contain at least two finite values >= -100%")
    if not isfinite(confidence_level) or not 0.5 <= confidence_level < 1:
        raise ValueError("confidence_level must be in [0.5, 1)")
    ordered = sorted(values)
    tail_count = max(1, ceil((1.0 - confidence_level) * len(ordered)))
    tail = ordered[:tail_count]
    return {
        "var_loss_fraction": -tail[-1],
        "cvar_loss_fraction": -(sum(tail) / len(tail)),
        "tail_observations": tail_count,
    }


def annualized_downside_deviation(
    returns: Sequence[float],
    target_return: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Annualized downside deviation using all observations in the denominator."""
    values = [float(value) for value in returns]
    if len(values) < 2 or any(not isfinite(value) or value < -1 for value in values):
        raise ValueError("returns must contain at least two finite values >= -100%")
    if not isfinite(target_return) or periods_per_year <= 0:
        raise ValueError("target_return or periods_per_year is invalid")
    shortfalls = [min(value - target_return, 0.0) for value in values]
    return sqrt(sum(value * value for value in shortfalls) / len(values)) * sqrt(
        periods_per_year
    )
