"""Deterministic portfolio analytics endpoints; no market-data claims are made here."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from atlas_api.domain.risk import (
    annualized_downside_deviation,\n    annualized_volatility,
    concentration_hhi,
    daily_returns,
    historical_var_cvar,\n    max_drawdown,
    portfolio_return,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class PriceSeriesRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    prices: list[float] = Field(min_length=2, max_length=5000)
    periods_per_year: int = Field(default=252, ge=1, le=366)


class AllocationRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    weights: list[float] = Field(min_length=1, max_length=500)
    asset_returns: list[float] = Field(min_length=1, max_length=500)



class ReturnsDistributionRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    returns: list[float] = Field(min_length=2, max_length=5000)
    confidence_level: float = Field(default=0.95, ge=0.5, lt=1.0)
    target_return: float = 0.0
    periods_per_year: int = Field(default=252, ge=1, le=366)


class WeightsRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    weights: list[float] = Field(min_length=1, max_length=500)


@router.post("/risk/price-series")
def analyze_price_series(request: PriceSeriesRequest) -> dict[str, object]:
    """Calculate historical statistics from caller-supplied chronological prices."""
    try:
        returns = daily_returns(request.prices)
        return {
            "observations": len(request.prices),
            "return_observations": len(returns),
            "daily_returns": returns,
            "annualized_volatility": annualized_volatility(
                returns, request.periods_per_year
            ),
            "max_drawdown": max_drawdown(request.prices),
            "methodology": "simple_close_to_close_returns_sample_stdev",
            "annualization_periods": request.periods_per_year,
            "data_source": "caller_supplied",
            "limitations": [
                "Historical statistics are not forecasts.",
                "No benchmark, fees, taxes, liquidity, or corporate-action adjustment is applied.",
                "Input prices must be chronological and consistently adjusted by the caller.",
            ],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/risk/allocation")
def analyze_allocation(request: AllocationRequest) -> dict[str, float]:
    """Calculate one-period portfolio return and long-only concentration."""
    try:
        result = {
            "weighted_return": portfolio_return(request.weights, request.asset_returns),
            "concentration_hhi": concentration_hhi(request.weights),
        }
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc



@router.post("/risk/returns-distribution")
def analyze_returns_distribution(
    request: ReturnsDistributionRequest,
) -> dict[str, object]:
    """Estimate empirical historical tail loss and downside deviation."""
    try:
        tail = historical_var_cvar(request.returns, request.confidence_level)
        return {
            **tail,
            "annualized_downside_deviation": annualized_downside_deviation(
                request.returns, request.target_return, request.periods_per_year
            ),
            "confidence_level": request.confidence_level,
            "periods_per_year": request.periods_per_year,
            "methodology": "nearest_rank_empirical_lower_tail",
            "limitations": [
                "Historical tail estimates are not forecasts or maximum-loss guarantees.",
                "Results depend strongly on sample length and market regime.",
                "No liquidity, gap, leverage, fee, tax, or transaction-cost adjustment is applied.",
            ],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/risk/concentration")
def analyze_concentration(request: WeightsRequest) -> dict[str, float]:
    try:
        return {"concentration_hhi": concentration_hhi(request.weights)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
