from typing import Any

import numpy as np
import pandas as pd
import ta

from app.services.market_data import get_ohlcv_dataframe


def _explain_rsi(value: float) -> str:
    if value >= 70:
        return (
            f"RSI {value:.1f} səviyyəsindədir — bu o deməkdir ki, səhmin qiyməti artıq çox yüksəlib "
            "və qısa müddətdə düzəliş ola bilər."
        )
    if value <= 30:
        return (
            f"RSI {value:.1f} səviyyəsindədir — bu o deməkdir ki, səhmin qiyməti çox aşağı düşüb "
            "və qısa müddətdə bərpa ola bilər."
        )
    return (
        f"RSI {value:.1f} neytral zonadadır — hələ həddindən artıq alınıb və ya satılıb deyil."
    )


def _explain_macd(macd: float, signal: float, histogram: float) -> str:
    if histogram > 0 and macd > signal:
        return "MACD yüksəliş siqnalı verir — alıcılar bazarda üstünlük təşkil edir."
    if histogram < 0 and macd < signal:
        return "MACD eniş siqnalı verir — satıcılar bazarda üstünlük təşkil edir."
    return "MACD neytraldır — aydın trend siqnalı yoxdur."


def _explain_ema(price: float, ema20: float, ema50: float, ema200: float) -> str:
    if price > ema20 > ema50 > ema200:
        return "Qiymət bütün EMA-ların üstündədir — güclü yüksəliş trendi mövcuddur."
    if price < ema20 < ema50 < ema200:
        return "Qiymət bütün EMA-ların altındadır — güclü eniş trendi mövcuddur."
    if price > ema200:
        return "Qiymət uzunmüddətli orta xəttin (EMA 200) üstündədir — ümumi trend müsbətdir."
    return "EMA-lar qarışıqdır — trend aydın deyil, diqqətli olmaq lazımdır."


def _explain_bollinger(price: float, upper: float, lower: float, middle: float) -> str:
    if price >= upper:
        return "Qiymət Bollinger üst zolağına yaxındır — həddindən artıq alınmış ola bilər."
    if price <= lower:
        return "Qiymət Bollinger alt zolağına yaxındır — həddindən artıq satılmış ola bilər."
    pct = (price - lower) / (upper - lower) * 100 if upper != lower else 50
    return f"Qiymət Bollinger zolaqlarının daxilindədir ({pct:.0f}% aralıqda) — normal hərəkət."


def _explain_volume(current_vol: float, avg_vol: float) -> str:
    ratio = current_vol / avg_vol if avg_vol else 1
    if ratio > 1.5:
        return f"Həcm ortalamadan {ratio:.1f}x yüksəkdir — güclü maraq və hərəkət var."
    if ratio < 0.7:
        return "Həcm aşağıdır — bazarda zəif maraq var, trend zəif ola bilər."
    return "Həcm normal səviyyədədir — standart bazar fəaliyyəti."


def calculate_technical_analysis() -> dict[str, Any]:
    df = get_ohlcv_dataframe(365)
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
    macd_ind = ta.trend.MACD(close)
    ema20 = ta.trend.EMAIndicator(close, window=20).ema_indicator()
    ema50 = ta.trend.EMAIndicator(close, window=50).ema_indicator()
    ema200 = ta.trend.EMAIndicator(close, window=200).ema_indicator()
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)

    current_price = float(close.iloc[-1])
    rsi_val = float(rsi.iloc[-1])
    macd_val = float(macd_ind.macd().iloc[-1])
    signal_val = float(macd_ind.macd_signal().iloc[-1])
    hist_val = float(macd_ind.macd_diff().iloc[-1])
    ema20_val = float(ema20.iloc[-1])
    ema50_val = float(ema50.iloc[-1])
    ema200_val = float(ema200.iloc[-1])
    bb_upper = float(bb.bollinger_hband().iloc[-1])
    bb_lower = float(bb.bollinger_lband().iloc[-1])
    bb_middle = float(bb.bollinger_mavg().iloc[-1])
    current_vol = float(volume.iloc[-1])
    avg_vol = float(volume.tail(20).mean())

    # Scores for signal engine (0-100 bullish bias)
    rsi_score = 50 + (50 - rsi_val) * 0.5 if rsi_val > 50 else 50 + (50 - rsi_val) * 0.3
    macd_score = 65 if hist_val > 0 else 35
    ema_score = 70 if current_price > ema200_val else 30
    bb_score = 35 if current_price >= bb_upper else 65 if current_price <= bb_lower else 50
    vol_score = 60 if current_vol > avg_vol and current_price > close.iloc[-2] else 40

    overall_bias = np.mean([rsi_score, macd_score, ema_score, bb_score, vol_score])

    return {
        "price": round(current_price, 2),
        "rsi": {"value": round(rsi_val, 2), "explanation": _explain_rsi(rsi_val)},
        "macd": {
            "macd": round(macd_val, 4),
            "signal": round(signal_val, 4),
            "histogram": round(hist_val, 4),
            "explanation": _explain_macd(macd_val, signal_val, hist_val),
        },
        "ema": {
            "ema20": round(ema20_val, 2),
            "ema50": round(ema50_val, 2),
            "ema200": round(ema200_val, 2),
            "explanation": _explain_ema(current_price, ema20_val, ema50_val, ema200_val),
        },
        "bollinger": {
            "upper": round(bb_upper, 2),
            "middle": round(bb_middle, 2),
            "lower": round(bb_lower, 2),
            "explanation": _explain_bollinger(current_price, bb_upper, bb_lower, bb_middle),
        },
        "volume": {
            "current": int(current_vol),
            "average_20d": int(avg_vol),
            "ratio": round(current_vol / avg_vol, 2) if avg_vol else 1,
            "explanation": _explain_volume(current_vol, avg_vol),
        },
        "technical_bias_score": round(float(overall_bias), 1),
    }
