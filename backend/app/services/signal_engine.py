from typing import Any

import numpy as np
import pandas as pd
import ta

from app.services.market_data import get_ohlcv_dataframe
from app.services.news_analysis import analyze_news, fetch_news
from app.services.technical_analysis import calculate_technical_analysis


SIGNAL_LABELS = {
    "very_strong_buy": "ÇOX GÜCLÜ AL",
    "buy": "AL",
    "hold": "GÖZLƏ",
    "sell": "SAT",
    "very_strong_sell": "ÇOX GÜCLÜ SAT",
}


def _calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    atr = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=period)
    return float(atr.average_true_range().iloc[-1])


def _score_to_signal(composite: float) -> tuple[str, str]:
    if composite >= 80:
        return "very_strong_buy", SIGNAL_LABELS["very_strong_buy"]
    if composite >= 65:
        return "buy", SIGNAL_LABELS["buy"]
    if composite >= 45:
        return "hold", SIGNAL_LABELS["hold"]
    if composite >= 30:
        return "sell", SIGNAL_LABELS["sell"]
    return "very_strong_sell", SIGNAL_LABELS["very_strong_sell"]


def _risk_level(composite: float, atr_pct: float) -> str:
    volatility_risk = atr_pct > 3
    if composite >= 70 and not volatility_risk:
        return "Aşağı"
    if composite <= 35 or volatility_risk:
        return "Yüksək"
    return "Orta"


def _build_reason(signal_key: str, tech: dict, news_prob: dict) -> str:
    reasons = {
        "very_strong_buy": (
            f"Texniki göstəricilər güclü yüksəliş ehtimalı göstərir ({tech['technical_bias_score']}/100). "
            f"Xəbər analizi: yüksəliş {news_prob.get('yüksəliş_ehtimalı', 50)}%."
        ),
        "buy": (
            f"Göstəricilər ümumilikdə müsbətdir. RSI və MACD alış istiqamətindədir. "
            f"Xəbər sentimenti: {news_prob.get('yüksəliş_ehtimalı', 50)}% müsbət."
        ),
        "hold": (
            "Bazar qarışıq siqnallar verir. Aydın istiqamət yoxdur — gözləmək daha məntiqli ola bilər. "
            "Yeni məlumat gələnə qədər ehtiyatlı olun."
        ),
        "sell": (
            f"Texniki göstəricilər zəifləmə əlamətləri göstərir ({tech['technical_bias_score']}/100). "
            f"Xəbər analizi: eniş ehtimalı {news_prob.get('eniş_ehtimalı', 30)}%."
        ),
        "very_strong_sell": (
            "Güclü eniş siqnalları mövcuddur. RSI yüksək, MACD mənfi, xəbərlər pessimistdir. "
            "Yüksək risk — ehtiyatlı olmaq vacibdir."
        ),
    }
    return reasons.get(signal_key, reasons["hold"])


async def generate_signal() -> dict[str, Any]:
    tech = calculate_technical_analysis()
    news = await fetch_news()
    news_stats = analyze_news(news)

    df = get_ohlcv_dataframe(90)
    price = tech["price"]
    atr = _calculate_atr(df)
    atr_pct = (atr / price) * 100

    tech_score = tech["technical_bias_score"]
    news_score = news_stats["news_bias_score"]
    composite = tech_score * 0.6 + news_score * 0.4

    signal_key, signal_label = _score_to_signal(composite)
    risk = _risk_level(composite, atr_pct)

    # Probability distribution
    if composite >= 70:
        bull, bear, neutral = 68, 20, 12
    elif composite >= 55:
        bull, bear, neutral = 55, 25, 20
    elif composite >= 45:
        bull, bear, neutral = 40, 35, 25
    elif composite >= 30:
        bull, bear, neutral = 25, 50, 25
    else:
        bull, bear, neutral = 15, 65, 20

    stop_loss = round(price - 2 * atr, 2)
    take_profit = round(price + 3 * atr, 2)

    return {
        "signal": signal_label,
        "signal_key": signal_key,
        "probability": signal_label,
        "confidence_pct": round(composite, 1),
        "probabilities": {
            "yüksəliş_ehtimalı": bull,
            "eniş_ehtimalı": bear,
            "neytral": neutral,
        },
        "risk_level": risk,
        "reason": _build_reason(signal_key, tech, news_stats["summary"]),
        "price": price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "atr": round(atr, 2),
        "atr_explanation": (
            f"Stop loss ATR ({atr:.2f}) əsasında hesablanıb — bu, orta gündəlik hərəkət həddidir. "
            f"2x ATR = ${stop_loss}, 3x ATR = ${take_profit} hədəf."
        ),
        "disclaimer": "Bu siqnal ehtimal əsaslı analizdir, investisiya məsləhəti deyil.",
    }
