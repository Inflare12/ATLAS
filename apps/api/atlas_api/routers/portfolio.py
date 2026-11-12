"""Deterministic portfolio analytics endpoints; no market-data claims are made here."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from atlas_api.domain.risk import (
    annualized_volatility,
    concentration_hhi,
    daily_returns,
    max_drawdown,
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


@router.post("/risk/concentration")
def analyze_concentration(request: WeightsRequest) -> dict[str, float]:
    try:
        return {"concentration_hhi": concentration_hhi(request.weights)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
