from datetime import datetime
from typing import Any

import httpx
import numpy as np
import pandas as pd

from app.config import settings
from app.redis_client import cache_delete, cache_get, cache_set

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

_master_df: pd.DataFrame | None = None
_last_live_fetch: datetime | None = None


def invalidate_cache() -> None:
    global _master_df, _last_live_fetch
    _master_df = None
    _last_live_fetch = None
    for key in (
        "nvda_master_history",
        "nvda_price_panel",
        "nvda_live_quote",
        "nvda_intraday",
        "nvda_yearly",
    ):
        cache_delete(key)


def _yahoo_chart(interval: str = "1d", range_: str = "2y") -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{settings.symbol}"
    try:
        with httpx.Client(timeout=10, headers=YAHOO_HEADERS) as client:
            resp = client.get(url, params={"interval": interval, "range": range_})
            resp.raise_for_status()
            data = resp.json()
            results = data.get("chart", {}).get("result")
            if not results:
                return None
            return results[0]
    except Exception:
        return None


def _chart_to_dataframe(result: dict) -> pd.DataFrame:
    timestamps = result["timestamp"]
    q = result["indicators"]["quote"][0]
    rows = []
    for i, ts in enumerate(timestamps):
        close = q.get("close", [None] * len(timestamps))[i]
        if close is None:
            continue
        rows.append({
            "Date": pd.Timestamp(ts, unit="s", tz="UTC").tz_convert(None),
            "Open": q.get("open", [close] * len(timestamps))[i] or close,
            "High": q.get("high", [close] * len(timestamps))[i] or close,
            "Low": q.get("low", [close] * len(timestamps))[i] or close,
            "Close": close,
            "Volume": int(q.get("volume", [0] * len(timestamps))[i] or 0),
        })
    df = pd.DataFrame(rows).set_index("Date")
    return df


def _get_master_df(force: bool = False) -> pd.DataFrame:
    global _master_df
    if _master_df is not None and not force:
        return _master_df

    if not force:
        cached = cache_get("nvda_master_history")
        if cached:
            df = pd.DataFrame(cached)
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)
            _master_df = df
            return df

    result = _yahoo_chart(interval="1d", range_="2y")
    if result:
        df = _chart_to_dataframe(result)
    else:
        df = pd.DataFrame()

    if df.empty:
        raise ValueError("NVDA məlumatları alına bilmədi — internet bağlantısını yoxlayın")

    records = df.reset_index()
    records["Date"] = records["Date"].astype(str)
    cache_set("nvda_master_history", records.to_dict(orient="records"), ttl=300)
    _master_df = df
    return df


def get_live_quote(force: bool = False) -> dict[str, Any]:
    cache_key = "nvda_live_quote"
    if not force:
        cached = cache_get(cache_key)
        if cached:
            return cached

    result = _yahoo_chart(interval="1m", range_="1d")
    if not result:
        meta_df = _get_master_df()
        current = float(meta_df["Close"].iloc[-1])
        prev = float(meta_df["Close"].iloc[-2]) if len(meta_df) > 1 else current
        quote = {
            "price": round(current, 2),
            "prev_close": round(prev, 2),
            "daily_change": round(current - prev, 2),
            "daily_change_pct": round((current - prev) / prev * 100, 2) if prev else 0,
            "volume": int(meta_df["Volume"].iloc[-1]),
            "market_state": "CLOSED",
            "data_source": "yahoo_finance_delayed",
        }
    else:
        meta = result["meta"]
        price = float(meta.get("regularMarketPrice") or meta.get("previousClose", 0))
        prev_close = float(meta.get("previousClose") or meta.get("chartPreviousClose") or price)
        change = price - prev_close
        quote = {
            "price": round(price, 2),
            "prev_close": round(prev_close, 2),
            "daily_change": round(change, 2),
            "daily_change_pct": round(change / prev_close * 100, 2) if prev_close else 0,
            "volume": int(meta.get("regularMarketVolume") or 0),
            "market_state": meta.get("marketState", "UNKNOWN"),
            "data_source": "yahoo_finance_live",
        }

    quote["symbol"] = settings.symbol
    quote["updated_at"] = datetime.utcnow().isoformat() + "Z"
    quote["is_market_active"] = quote.get("market_state") in ("REGULAR", "PRE", "POST")
    if not force:
        cache_set(cache_key, quote, ttl=1)
    return quote


def get_price_panel(force: bool = False) -> dict[str, Any]:
    live = get_live_quote(force=force)
    df = _get_master_df(force=force)

    week_start = float(df["Close"].iloc[-5]) if len(df) >= 5 else live["price"]
    week_change_pct = ((live["price"] - week_start) / week_start) * 100 if week_start else 0

    if week_change_pct > 2:
        week_trend, week_trend_az = "Yüksəliş", "Son həftə qiymət artım trendindədir"
    elif week_change_pct < -2:
        week_trend, week_trend_az = "Eniş", "Son həftə qiymət eniş trendindədir"
    else:
        week_trend, week_trend_az = "Neytral", "Son həftə qiymət sabit hərəkət edir"

    market_open = live.get("market_state") == "REGULAR"
    source_label = "Yahoo Finance (canlı)" if market_open else "Yahoo Finance (15 dəq. gecikmə)"

    return {
        "symbol": settings.symbol,
        "name": "NVIDIA Corporation",
        "price": live["price"],
        "daily_change": live["daily_change"],
        "daily_change_pct": live["daily_change_pct"],
        "week_change_pct": round(week_change_pct, 2),
        "week_trend": week_trend,
        "week_trend_explanation": week_trend_az,
        "volume": live["volume"],
        "market_cap": None,
        "market_state": live.get("market_state", "UNKNOWN"),
        "updated_at": live["updated_at"],
        "data_source": source_label,
    }


def get_intraday_chart(force: bool = False) -> list[dict[str, Any]]:
    cache_key = "nvda_intraday"
    if not force:
        cached = cache_get(cache_key)
        if cached:
            return cached

    result = _yahoo_chart(interval="1m", range_="1d")
    if not result:
        return get_chart_data(1, force=force)

    df = _chart_to_dataframe(result)
    chart = [
        {
            "date": idx.strftime("%H:%M"),
            "timestamp": idx.isoformat(),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for idx, row in df.iterrows()
    ]
    cache_set(cache_key, chart, ttl=10)
    return chart


def get_yearly_chart(force: bool = False) -> list[dict[str, Any]]:
    cache_key = "nvda_yearly"
    if not force:
        cached = cache_get(cache_key)
        if cached:
            return cached

    result = _yahoo_chart(interval="1d", range_="1y")
    if result:
        df = _chart_to_dataframe(result)
    else:
        df = _get_master_df(force=force).tail(365)

    chart = [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "timestamp": idx.isoformat(),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for idx, row in df.iterrows()
    ]
    cache_set(cache_key, chart, ttl=3600)
    return chart


def get_chart_data(days: int = 90, force: bool = False) -> list[dict[str, Any]]:
    if days >= 365:
        return get_yearly_chart(force=force)
    if days <= 1:
        return get_intraday_chart(force=force)

    df = _get_master_df(force=force).tail(days)
    return [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "timestamp": idx.isoformat(),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for idx, row in df.iterrows()
    ]


def get_ohlcv_dataframe(days: int = 365, force: bool = False) -> pd.DataFrame:
    return _get_master_df(force=force).tail(days).copy()
