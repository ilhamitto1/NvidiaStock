from typing import Any

from app.services.comprehensive_analysis import run_comprehensive_analysis


def build_daily_forecast(tech: dict, signal: dict, news: list[dict] | None = None) -> dict[str, Any]:
    """Əvvəlki API uyğunluğu — hərtərəfli analizdən istifadə edir."""
    if news is not None:
        result = run_comprehensive_analysis(news, force=False)
        return result["daily_forecast"]

    # Fallback — signal-dən
    from app.services.market_data import get_live_quote
    import ta
    from app.services.market_data import get_ohlcv_dataframe
    from datetime import datetime

    quote = get_live_quote(force=False)
    price = quote["price"]
    df = get_ohlcv_dataframe(90)
    atr = float(
        ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14)
        .average_true_range().iloc[-1]
    )
    probs = signal["probabilities"]
    today = datetime.utcnow().strftime("%d.%m.%Y")

    return {
        "date": today,
        "current_price": price,
        "range_low": round(price - atr * 0.85, 2),
        "range_high": round(price + atr * 0.85, 2),
        "range_very_low": round(price - atr * 1.8, 2),
        "range_very_high": round(price + atr * 1.8, 2),
        "probabilities": {"qalxma": probs["yüksəliş_ehtimalı"], "enme": probs["eniş_ehtimalı"], "sabit": probs["neytral"]},
        "mood": "",
        "summary": f"Bu gün NVDA təxminən ${round(price - atr, 2)} — ${round(price + atr, 2)} arasında.",
        "summary_simple": signal.get("reason", ""),
        "note": "Bu yalnız təxminidir.",
        "for_user": "Famil Dosdiyev",
    }
