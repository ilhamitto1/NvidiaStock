from typing import Any

import pandas as pd
import ta

from app.services.market_data import get_ohlcv_dataframe
from app.services.news_analysis import analyze_news
from app.services.signal_engine import (
    SIGNAL_LABELS,
    _build_reason,
    _calculate_atr,
    _risk_level,
    _score_to_signal,
)


def build_signal(tech: dict, news_stats: dict) -> dict[str, Any]:
    df = get_ohlcv_dataframe(90)
    price = tech["price"]
    atr = _calculate_atr(df)
    atr_pct = (atr / price) * 100

    composite = tech["technical_bias_score"] * 0.6 + news_stats["news_bias_score"] * 0.4
    signal_key, signal_label = _score_to_signal(composite)
    risk = _risk_level(composite, atr_pct)

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


def build_sentiment(news: list[dict], news_stats: dict) -> dict[str, Any]:
    bullish_factors = []
    bearish_factors = []
    risk_factors = []

    for article in news:
        factor = {
            "title": article["title"],
            "strength": article["impact_strength"],
            "category": article["category"],
        }
        if article["sentiment"] == "müsbət" and article["impact_strength"] >= 60:
            bullish_factors.append({
                **factor,
                "explanation": f"Bu xəbər yaxşı xəbərdir (güc: {article['impact_strength']}/100).",
            })
        elif article["sentiment"] == "mənfi" and article["impact_strength"] >= 50:
            bearish_factors.append({
                **factor,
                "explanation": f"Bu xəbər pis təsir edə bilər (güc: {article['impact_strength']}/100).",
            })
        if article["impact_strength"] >= 70:
            risk_factors.append({
                **factor,
                "explanation": "Yüksək təsir gücü — qiymətə qısa müddətli güclü reaksiya ola bilər.",
            })

    if not bullish_factors:
        bullish_factors.append({
            "title": "Texniki göstəricilər nəzərə alınmalıdır",
            "strength": 50,
            "category": "Ümumi",
            "explanation": "Son xəbərlərdə güclü müsbət siqnal aşkar edilmədi.",
        })

    sentiment_score = news_stats["news_bias_score"]
    if sentiment_score >= 65:
        mood, mood_az = "Yaxşı", "Xəbərlər ümumilikdə yaxşıdır — investorlar NVIDIA-ya inanır."
    elif sentiment_score <= 35:
        mood, mood_az = "Pis", "Xəbərlər pisdir — ehtiyatlı olmaq lazımdır."
    else:
        mood, mood_az = "Qarışıq", "Xəbərlər qarışıqdır — aydın deyil."

    return {
        "mood": mood,
        "mood_explanation": mood_az,
        "probabilities": news_stats["summary"],
        "sentiment_score": sentiment_score,
        "bullish_factors": bullish_factors[:5],
        "bearish_factors": bearish_factors[:5],
        "risk_factors": risk_factors[:5],
        "disclaimer": "Bu sentiment analizi ehtimal əsaslıdır, gələcək qiymət zəmanəti deyil.",
    }


def build_risk(capital: float, signal: dict, df: pd.DataFrame) -> dict[str, Any]:
    atr = ta.volatility.AverageTrueRange(
        df["High"], df["Low"], df["Close"], window=14
    ).average_true_range().iloc[-1]
    price = signal["price"]
    atr_pct = (atr / price) * 100

    risk_pct_map = {"Aşağı": 1.0, "Orta": 2.0, "Yüksək": 3.0}
    risk_pct = risk_pct_map.get(signal["risk_level"], 2.0)

    recommended_investment = round(capital * (risk_pct / 100) * 10, 2)
    recommended_investment = min(recommended_investment, capital * 0.25)

    stop_distance = price - signal["stop_loss"]
    shares = int(recommended_investment / price) if price else 0
    actual_investment = round(shares * price, 2)
    max_loss_at_stop = round(shares * stop_distance, 2) if shares else 0
    max_loss = round(recommended_investment * (atr_pct / 100) * 2, 2)

    risk_score = min(100, round(atr_pct * 15 + (100 - signal["confidence_pct"]) * 0.3, 1))

    if risk_score >= 70:
        risk_summary = "Yüksək volatillik — kiçik investisiya ölçüsü tövsiyə olunur."
    elif risk_score >= 40:
        risk_summary = "Orta səviyyəli risk — balanslaşdırılmış yanaşma məqsədəuyğundur."
    else:
        risk_summary = "Aşağı risk — bazar nisbətən sabitdir, amma ehtiyatlı olun."

    return {
        "capital": capital,
        "risk_level": signal["risk_level"],
        "risk_score": risk_score,
        "risk_summary": risk_summary,
        "recommended_investment_pct": round(recommended_investment / capital * 100, 1),
        "recommended_investment_usd": round(recommended_investment, 2),
        "max_loss_usd": max_loss_at_stop or max_loss,
        "max_loss_pct_of_capital": round((max_loss_at_stop or max_loss) / capital * 100, 2),
        "atr_pct": round(atr_pct, 2),
        "stop_loss": signal["stop_loss"],
        "take_profit": signal["take_profit"],
        "shares_suggested": shares,
        "actual_investment": actual_investment,
        "explanation": (
            f"${capital:,.0f} kapitalınız varsa, tövsiyə olunan investisiya "
            f"${recommended_investment:,.0f} ({recommended_investment/capital*100:.1f}%) həcmindədir. "
            f"Stop loss səviyyəsində maksimum itki təxminən ${max_loss_at_stop or max_loss:,.0f} ola bilər."
        ),
        "disclaimer": "Bu risk hesablaması ehtimal əsaslıdır, maliyyə məsləhəti deyil.",
    }
