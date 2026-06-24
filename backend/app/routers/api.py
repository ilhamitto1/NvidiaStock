import asyncio
import json
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.services.backtest import run_backtest
from app.services.comprehensive_analysis import run_comprehensive_analysis
from app.services.daily_forecast import build_daily_forecast
from app.services.dashboard_service import build_risk, build_sentiment, build_signal
from app.services.market_data import (
    get_chart_data,
    get_intraday_chart,
    get_live_quote,
    get_ohlcv_dataframe,
    get_price_panel,
    get_yearly_chart,
    invalidate_cache,
)
from app.services.news_analysis import analyze_news, fetch_news
from app.services.risk_management import calculate_risk
from app.services.sentiment_analysis import get_sentiment_analysis
from app.services.signal_engine import generate_signal
from app.services.technical_analysis import calculate_technical_analysis
from app.schemas.models import RiskRequest
from app.redis_client import cache_delete, cache_get, cache_set

router = APIRouter(prefix="/api", tags=["NVDA Trading Intelligence"])


@router.get("/health")
async def health():
    return {"status": "ok", "message": "NVDA AI Trading Intelligence sistemi işləyir"}


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """Bazar açıq olanda hər saniyə canlı qiymət axını."""
    await websocket.accept()
    try:
        while True:
            quote = get_live_quote(force=True)
            intraday = get_intraday_chart(force=True)
            is_active = quote.get("is_market_active", False)

            payload: dict[str, Any] = {
                "type": "tick",
                "quote": quote,
                "intraday": intraday,
                "market_active": is_active,
                "interval_sec": 1 if is_active else 30,
            }
            await websocket.send_text(json.dumps(payload, default=str))

            await asyncio.sleep(1 if is_active else 30)
    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass


@router.get("/price")
async def price(refresh: bool = False):
    return get_price_panel(force=refresh)


@router.get("/live")
async def live(refresh: bool = False):
    quote = get_live_quote(force=refresh)
    intraday = get_intraday_chart(force=refresh)
    yearly = get_yearly_chart()
    return {"quote": quote, "intraday": intraday, "yearly": yearly}


@router.get("/chart")
async def chart(days: int = 90, refresh: bool = False):
    return get_chart_data(days, force=refresh)


@router.get("/chart/yearly")
async def chart_yearly(refresh: bool = False):
    return get_yearly_chart(force=refresh)


@router.get("/technical")
async def technical():
    return calculate_technical_analysis()


@router.get("/news")
async def news():
    return await fetch_news()


@router.get("/sentiment")
async def sentiment():
    return await get_sentiment_analysis()


@router.get("/signal")
async def signal():
    return await generate_signal()


@router.get("/backtest/{days}")
async def backtest(days: int):
    if days not in (30, 90):
        days = 30
    return run_backtest(days)


@router.post("/risk")
async def risk(body: RiskRequest):
    return await calculate_risk(body.capital)


@router.get("/dashboard")
async def dashboard(capital: float = 10000, refresh: bool = Query(False)):
    cache_key = f"dashboard_v2_{int(capital)}"
    if refresh:
        invalidate_cache()
        cache_delete(cache_key)
    else:
        cached = cache_get(cache_key)
        if cached:
            return cached

    price = get_price_panel(force=refresh)
    news = await fetch_news()
    news_stats = analyze_news(news)
    technical = calculate_technical_analysis()
    ohlcv = get_ohlcv_dataframe(90, force=refresh)

    # Hərtərəfli analiz — bütün qrafiklər + xəbərlər + texniki
    comprehensive = run_comprehensive_analysis(news, force=refresh)
    signal = comprehensive["signal"]
    daily_forecast = comprehensive["daily_forecast"]
    sentiment = build_sentiment(news, news_stats)
    backtest_30 = run_backtest(30)
    backtest_90 = run_backtest(90)
    risk = build_risk(capital, signal, ohlcv)
    chart = get_intraday_chart(force=refresh)
    chart_yearly = get_yearly_chart(force=refresh)

    result = {
        "price": price,
        "signal": signal,
        "daily_forecast": daily_forecast,
        "technical": technical,
        "sentiment": sentiment,
        "news": news,
        "backtest_30": backtest_30,
        "backtest_90": backtest_90,
        "risk": risk,
        "chart": chart,
        "chart_yearly": chart_yearly,
        "analysis_report": {
            "steps": comprehensive["analysis_steps"],
            "yearly": comprehensive["yearly_analysis"],
            "news": comprehensive["news_analysis"],
            "intraday": comprehensive["intraday_analysis"],
            "composite_score": comprehensive["composite_score"],
        },
    }
    cache_set(cache_key, result, ttl=15)
    return result
