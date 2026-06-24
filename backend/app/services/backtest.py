from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import ta

from app.services.market_data import get_ohlcv_dataframe


def _generate_historical_signal(close: pd.Series, idx: int) -> tuple[str, float]:
    window = close.iloc[max(0, idx - 50):idx + 1]
    if len(window) < 20:
        return "GÖZLƏ", 50.0

    rsi = ta.momentum.RSIIndicator(window, window=14).rsi().iloc[-1]
    macd_ind = ta.trend.MACD(window)
    hist = macd_ind.macd_diff().iloc[-1]
    ema20 = ta.trend.EMAIndicator(window, window=20).ema_indicator().iloc[-1]
    price = window.iloc[-1]

    score = 50.0
    if rsi < 40:
        score += 15
    elif rsi > 70:
        score -= 15
    if hist > 0:
        score += 10
    else:
        score -= 10
    if price > ema20:
        score += 10
    else:
        score -= 10

    if score >= 70:
        return "AL", score
    if score >= 55:
        return "AL", score
    if score >= 45:
        return "GÖZLƏ", score
    if score >= 30:
        return "SAT", score
    return "SAT", score


def run_backtest(days: int = 30) -> dict[str, Any]:
    df = get_ohlcv_dataframe(max(days + 60, 120))
    close = df["Close"]
    results = []

    start_idx = len(close) - days
    for i in range(start_idx, len(close) - 5):
        signal, score = _generate_historical_signal(close, i)
        entry = float(close.iloc[i])
        exit_price = float(close.iloc[i + 5])
        pnl_pct = ((exit_price - entry) / entry) * 100

        if signal in ("AL", "ÇOX GÜCLÜ AL"):
            success = pnl_pct > 0
        elif signal in ("SAT", "ÇOX GÜCLÜ SAT"):
            success = pnl_pct < 0
        else:
            success = abs(pnl_pct) < 2

        results.append({
            "date": close.index[i].strftime("%Y-%m-%d"),
            "signal": signal,
            "entry_price": round(entry, 2),
            "exit_price": round(exit_price, 2),
            "pnl_pct": round(pnl_pct, 2),
            "success": success,
            "score": round(score, 1),
        })

    if not results:
        return {
            "period_days": days,
            "total_signals": 0,
            "success_rate": 0,
            "loss_rate": 0,
            "avg_return_pct": 0,
            "signals": [],
            "disclaimer": "Bu yalnız tarixi analizdir, gələcək zəmanət deyil.",
        }

    successes = sum(1 for r in results if r["success"])
    total = len(results)
    avg_return = np.mean([r["pnl_pct"] for r in results if r["signal"] != "GÖZLƏ"]) if results else 0

    buy_signals = [r for r in results if r["signal"] == "AL"]
    buy_success = sum(1 for r in buy_signals if r["success"]) / len(buy_signals) * 100 if buy_signals else 0

    return {
        "period_days": days,
        "total_signals": total,
        "success_rate": round(successes / total * 100, 1),
        "loss_rate": round((total - successes) / total * 100, 1),
        "avg_return_pct": round(float(avg_return), 2),
        "buy_success_rate": round(buy_success, 1),
        "signals": results[-20:],
        "disclaimer": "Bu yalnız tarixi analizdir, gələcək zəmanət deyil.",
    }
