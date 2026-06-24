from typing import Any

from pydantic import BaseModel


class PricePanel(BaseModel):
    symbol: str
    name: str
    price: float
    daily_change: float
    daily_change_pct: float
    week_change_pct: float
    week_trend: str
    week_trend_explanation: str
    volume: int
    market_cap: int | None = None
    updated_at: str


class Probabilities(BaseModel):
    yüksəliş_ehtimalı: float
    eniş_ehtimalı: float
    neytral: float


class SignalResponse(BaseModel):
    signal: str
    signal_key: str
    confidence_pct: float
    probabilities: Probabilities
    risk_level: str
    reason: str
    price: float
    stop_loss: float
    take_profit: float
    atr: float
    atr_explanation: str
    disclaimer: str


class RiskRequest(BaseModel):
    capital: float = 10000


class DashboardResponse(BaseModel):
    price: dict[str, Any]
    signal: dict[str, Any]
    technical: dict[str, Any]
    sentiment: dict[str, Any]
    news: list[dict[str, Any]]
    backtest_30: dict[str, Any]
    backtest_90: dict[str, Any]
    risk: dict[str, Any]
    chart: list[dict[str, Any]]
