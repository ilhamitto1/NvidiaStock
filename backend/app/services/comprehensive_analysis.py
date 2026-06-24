"""
NVDA hərtərəfli analiz mühərriki.
Bütün qrafikləri, xəbərləri və texniki göstəriciləri birləşdirir.
"""

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import ta

from app.services.market_data import (
    get_intraday_chart,
    get_live_quote,
    get_ohlcv_dataframe,
)
from app.services.signal_engine import _risk_level, _score_to_signal
from app.services.technical_analysis import calculate_technical_analysis


def _analyze_yearly_chart(df: pd.DataFrame) -> dict[str, Any]:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    price = float(close.iloc[-1])

    year_high = float(high.max())
    year_low = float(low.min())
    year_start = float(close.iloc[0])
    year_change_pct = ((price - year_start) / year_start) * 100

    high_52w = float(high.tail(252).max()) if len(high) >= 50 else year_high
    low_52w = float(low.tail(252).min()) if len(low) >= 50 else year_low

    position_in_range = (price - low_52w) / (high_52w - low_52w) * 100 if high_52w != low_52w else 50

    # Dəstək / müqavimət — son 60 günün pivotları
    recent = df.tail(60)
    support = float(recent["Low"].min())
    resistance = float(recent["High"].max())

    sma20 = float(close.tail(20).mean())
    sma50 = float(close.tail(50).mean()) if len(close) >= 50 else sma20
    sma200 = float(close.tail(200).mean()) if len(close) >= 200 else sma50

    daily_returns = close.pct_change().dropna()
    volatility_pct = float(daily_returns.tail(30).std() * 100) if len(daily_returns) > 5 else 2.0

    # İllik trend balı
    score = 50.0
    if price > sma200:
        score += 15
    if price > sma50:
        score += 10
    if sma20 > sma50:
        score += 8
    if year_change_pct > 10:
        score += 12
    elif year_change_pct < -10:
        score -= 12
    if position_in_range > 80:
        score -= 8  # yüksək zonada — düzəliş riski
    elif position_in_range < 20:
        score += 8  # aşağı zonada — bərpa potensialı

    if year_change_pct > 5:
        trend_az = f"Son ildə qiymət {year_change_pct:.1f}% qalxıb — ümumi trend yüksəliş istiqamətindədir."
    elif year_change_pct < -5:
        trend_az = f"Son ildə qiymət {abs(year_change_pct):.1f}% enib — ümumi trend zəifdir."
    else:
        trend_az = f"Son ildə qiymət təxminən {year_change_pct:+.1f}% dəyişib — trend sabitdir."

    return {
        "year_high": round(year_high, 2),
        "year_low": round(year_low, 2),
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "year_change_pct": round(year_change_pct, 2),
        "position_in_range_pct": round(position_in_range, 1),
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "sma200": round(sma200, 2),
        "volatility_pct": round(volatility_pct, 2),
        "trend_score": round(min(100, max(0, score)), 1),
        "trend_explanation": trend_az,
    }


def _analyze_intraday(intraday: list[dict], quote: dict) -> dict[str, Any]:
    if not intraday:
        return {"intraday_score": 50, "intraday_explanation": "Bu gün üçün intraday məlumat yoxdur.", "today_change_pct": 0}

    closes = [p["close"] for p in intraday]
    highs = [p["high"] for p in intraday]
    lows = [p["low"] for p in intraday]

    today_open = intraday[0]["open"]
    today_high = max(highs)
    today_low = min(lows)
    current = quote["price"]
    today_change = ((current - today_open) / today_open) * 100 if today_open else 0

    score = 50.0
    if today_change > 1:
        score += 15
    elif today_change < -1:
        score -= 15
    if current > today_open:
        score += 5
    else:
        score -= 5

    # Son 30 dəqiqə momentum
    if len(closes) >= 30:
        recent_mom = (closes[-1] - closes[-30]) / closes[-30] * 100
        if recent_mom > 0.3:
            score += 8
        elif recent_mom < -0.3:
            score -= 8

    if today_change > 0:
        expl = f"Bu gün bazar açılandan bəri qiymət {today_change:+.2f}% dəyişib — gün üzrə yüksəliş var."
    elif today_change < 0:
        expl = f"Bu gün bazar açılandan bəri qiymət {today_change:.2f}% enib — gün üzrə zəiflik var."
    else:
        expl = "Bu gün qiymət demək olar ki, dəyişməyib."

    return {
        "today_open": round(today_open, 2),
        "today_high": round(today_high, 2),
        "today_low": round(today_low, 2),
        "today_change_pct": round(today_change, 2),
        "intraday_score": round(min(100, max(0, score)), 1),
        "intraday_explanation": expl,
    }


def _analyze_news_deep(news: list[dict]) -> dict[str, Any]:
    if not news:
        return {
            "news_score": 50,
            "weighted_sentiment": 0,
            "positive_weight": 0,
            "negative_weight": 0,
            "article_count": 0,
            "explanation": "Xəbər tapılmadı — yalnız qrafik analizi istifadə olunur.",
            "key_positive": [],
            "key_negative": [],
        }

    pos_weight = sum(a["impact_strength"] for a in news if a["sentiment"] == "müsbət")
    neg_weight = sum(a["impact_strength"] for a in news if a["sentiment"] == "mənfi")
    neu_weight = sum(a["impact_strength"] for a in news if a["sentiment"] not in ("müsbət", "mənfi"))
    total = pos_weight + neg_weight + neu_weight or 1

    weighted_sentiment = (pos_weight - neg_weight) / total  # -1 to 1
    news_score = 50 + weighted_sentiment * 40
    news_score = min(100, max(0, news_score))

    pos_articles = sorted(
        [a for a in news if a["sentiment"] == "müsbət"],
        key=lambda x: x["impact_strength"],
        reverse=True,
    )[:3]
    neg_articles = sorted(
        [a for a in news if a["sentiment"] == "mənfi"],
        key=lambda x: x["impact_strength"],
        reverse=True,
    )[:3]

    pos_count = sum(1 for a in news if a["sentiment"] == "müsbət")
    neg_count = sum(1 for a in news if a["sentiment"] == "mənfi")

    if pos_count > neg_count * 1.5:
        expl = (
            f"{len(news)} xəbər analiz edildi: {pos_count} müsbət, {neg_count} mənfi. "
            "Xəbər axını ümumilikdə NVDA üçün müsbət təsir göstərir."
        )
    elif neg_count > pos_count * 1.5:
        expl = (
            f"{len(news)} xəbər analiz edildi: {pos_count} müsbət, {neg_count} mənfi. "
            "Xəbər axını NVDA üçün mənfi təzyiq yarada bilər."
        )
    else:
        expl = (
            f"{len(news)} xəbər analiz edildi: {pos_count} müsbət, {neg_count} mənfi. "
            "Xəbərlər qarışıqdır — aydın istiqamət yoxdur."
        )

    return {
        "news_score": round(news_score, 1),
        "weighted_sentiment": round(weighted_sentiment, 3),
        "positive_weight": round(pos_weight, 1),
        "negative_weight": round(neg_weight, 1),
        "article_count": len(news),
        "positive_count": pos_count,
        "negative_count": neg_count,
        "explanation": expl,
        "key_positive": [{"title": a["title"], "strength": a["impact_strength"]} for a in pos_articles],
        "key_negative": [{"title": a["title"], "strength": a["impact_strength"]} for a in neg_articles],
    }


def _compute_probabilities(
    tech_score: float,
    news_score: float,
    yearly_score: float,
    intraday_score: float,
) -> dict[str, float]:
    """Çəki əsaslı real ehtimal hesablaması."""
    composite = (
        tech_score * 0.30
        + news_score * 0.30
        + yearly_score * 0.25
        + intraday_score * 0.15
    )

    # Composite-dən ehtimal paylanması
    bull_raw = max(0, (composite - 40) * 1.5)
    bear_raw = max(0, (60 - composite) * 1.5)
    neutral_raw = max(10, 100 - bull_raw - bear_raw)

    total = bull_raw + bear_raw + neutral_raw
    bull = round(bull_raw / total * 100, 1)
    bear = round(bear_raw / total * 100, 1)
    neutral = round(100 - bull - bear, 1)

    return {
        "yüksəliş_ehtimalı": bull,
        "eniş_ehtimalı": bear,
        "neytral": neutral,
        "composite_score": round(composite, 1),
    }


def _compute_price_range(
    price: float,
    df: pd.DataFrame,
    yearly: dict,
    tech: dict,
    news_deep: dict,
    probabilities: dict,
) -> dict[str, float]:
    """ATR + dəstək/müqavimət + xəbər biası ilə real aralıq."""
    atr = float(
        ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14)
        .average_true_range()
        .iloc[-1]
    )

    bb_lower = tech["bollinger"]["lower"]
    bb_upper = tech["bollinger"]["upper"]

    support = yearly["support"]
    resistance = yearly["resistance"]
    low_52w = yearly["low_52w"]

    # Xəbər və kompozit bias — mərkəzi sürüşdür
    bias = news_deep["weighted_sentiment"] * 0.4 + (probabilities["composite_score"] - 50) / 100 * 0.3
    expected_center = price + bias * atr

    # Günlük aralıq — ATR və volatillik
    vol_mult = 1.0 + yearly["volatility_pct"] / 100
    half_range = atr * vol_mult * 0.85

    range_low = expected_center - half_range
    range_high = expected_center + half_range

    # Dəstək/müqavimətə clamp
    range_low = max(range_low, support * 0.995, bb_lower * 0.99, low_52w * 0.98)
    range_high = min(range_high, resistance * 1.005, bb_upper * 1.01, yearly["high_52w"] * 1.01)

    # Əmin ol ki, cari qiymət aralıqda
    range_low = min(range_low, price - 0.01)
    range_high = max(range_high, price + 0.01)

    very_low = max(range_low - atr * 0.8, low_52w * 0.97)
    very_high = min(range_high + atr * 0.8, yearly["high_52w"] * 1.02)

    return {
        "range_low": round(range_low, 2),
        "range_high": round(range_high, 2),
        "range_very_low": round(very_low, 2),
        "range_very_high": round(very_high, 2),
        "atr": round(atr, 2),
        "expected_center": round(expected_center, 2),
    }


def _build_analysis_steps(
    yearly: dict,
    intraday: dict,
    news_deep: dict,
    tech: dict,
    probabilities: dict,
) -> list[dict[str, str]]:
    """Sadə AZ dilində analiz addımları."""
    steps = [
        {
            "title": "1. İllik qrafik analizi",
            "text": (
                f"{yearly['trend_explanation']} "
                f"52 həftəlik diapazon: ${yearly['low_52w']} — ${yearly['high_52w']}. "
                f"İndi qiymət bu diapazonun {yearly['position_in_range_pct']:.0f}%-indədir. "
                f"Dəstək: ${yearly['support']}, müqavimət: ${yearly['resistance']}."
            ),
        },
        {
            "title": "2. Bu günün qrafiki",
            "text": intraday["intraday_explanation"],
        },
        {
            "title": "3. Xəbər analizi",
            "text": news_deep["explanation"],
        },
        {
            "title": "4. Texniki göstəricilər",
            "text": (
                f"RSI: {tech['rsi']['explanation']} "
                f"MACD: {tech['macd']['explanation']} "
                f"Həcm: {tech['volume']['explanation']}"
            ),
        },
        {
            "title": "5. Ümumi nəticə",
            "text": (
                f"Bütün məlumatlar birləşdirildi. Ümumi bal: {probabilities['composite_score']}/100. "
                f"Qalxma ehtimalı: {probabilities['yüksəliş_ehtimalı']}%, "
                f"enmə: {probabilities['eniş_ehtimalı']}%, "
                f"dəyişməz: {probabilities['neytral']}%."
            ),
        },
    ]
    return steps


def _build_signal_reason_simple(
    signal_key: str,
    yearly: dict,
    news_deep: dict,
    probabilities: dict,
) -> str:
    reasons = {
        "very_strong_buy": (
            f"İllik trend güclü (+{yearly['year_change_pct']:.1f}%), xəbərlər müsbətdir, "
            f"texniki göstəricilər alış istiqamətindədir."
        ),
        "buy": (
            f"Ümumi bal {probabilities['composite_score']}/100. "
            f"Xəbərlər: {news_deep['positive_count']} müsbət, {news_deep['negative_count']} mənfi."
        ),
        "hold": (
            "Qrafiklər və xəbərlər qarışıq siqnal verir. Aydın istiqamət yoxdur — gözləmək məqsədəuyğundur."
        ),
        "sell": (
            f"Texniki zəiflik və mənfi xəbərlər ({news_deep['negative_count']} ədəd) "
            f"eniş ehtimalını artırır."
        ),
        "very_strong_sell": (
            "Güclü eniş siqnalları: illik trend zəifləyir, xəbərlər pessimist, texniki göstəricilər mənfi."
        ),
    }
    return reasons.get(signal_key, reasons["hold"])


def run_comprehensive_analysis(
    news: list[dict],
    force: bool = False,
) -> dict[str, Any]:
    """Bütün mənbələri analiz edib vahid nəticə qaytarır."""
    quote = get_live_quote(force=force)
    price = quote["price"]

    df = get_ohlcv_dataframe(365, force=force)
    intraday_data = get_intraday_chart(force=force)
    tech = calculate_technical_analysis()

    yearly = _analyze_yearly_chart(df)
    intraday = _analyze_intraday(intraday_data, quote)
    news_deep = _analyze_news_deep(news)

    probabilities = _compute_probabilities(
        tech["technical_bias_score"],
        news_deep["news_score"],
        yearly["trend_score"],
        intraday["intraday_score"],
    )

    price_range = _compute_price_range(price, df, yearly, tech, news_deep, probabilities)

    composite = probabilities["composite_score"]
    signal_key, signal_label = _score_to_signal(composite)
    atr_pct = price_range["atr"] / price * 100
    risk = _risk_level(composite, atr_pct)

    stop_loss = round(price - 2 * price_range["atr"], 2)
    take_profit = round(price + 2.5 * price_range["atr"], 2)

    analysis_steps = _build_analysis_steps(yearly, intraday, news_deep, tech, probabilities)

    bull = probabilities["yüksəliş_ehtimalı"]
    bear = probabilities["eniş_ehtimalı"]
    neutral = probabilities["neytral"]

    if bull >= 55:
        mood_simple = (
            f"Analiz göstərir ki, bu gün qalxma ehtimalı {bull}% dir. "
            f"Xəbərlər və illik qrafik bunu dəstəkləyir."
        )
    elif bear >= 55:
        mood_simple = (
            f"Analiz göstərir ki, bu gün enmə ehtimalı {bear}% dir. "
            f"Xəbərlər və qrafiklər ehtiyatlı olmağı tövsiyə edir."
        )
    else:
        mood_simple = (
            f"Bu gün dəyişməz qalma ehtimalı {neutral}% dir. "
            f"Aydın istiqamət yoxdur — gözləmək olar."
        )

    today = datetime.utcnow().strftime("%d.%m.%Y")

    daily_forecast = {
        "date": today,
        "current_price": price,
        "range_low": price_range["range_low"],
        "range_high": price_range["range_high"],
        "range_very_low": price_range["range_very_low"],
        "range_very_high": price_range["range_very_high"],
        "probabilities": {
            "qalxma": bull,
            "enme": bear,
            "sabit": neutral,
        },
        "mood": "yüksələ bilər" if bull >= 55 else "düşə bilər" if bear >= 55 else "sabit qala bilər",
        "summary": (
            f"Detallı analizdən sonra: bu gün ({today}) NVDA təxminən "
            f"${price_range['range_low']} — ${price_range['range_high']} arasında ola bilər. "
            f"Cari qiymət: ${price}."
        ),
        "summary_simple": mood_simple,
        "note": (
            "Bu aralıq illik qrafik, bu günün qrafiki, xəbərlər və texniki göstəricilər "
            "birlikdə analiz edilərək hesablanıb. Dəqiq qiymət zəmanət deyil."
        ),
        "for_user": "Famil Dosdiyev",
        "analysis_basis": {
            "yearly_trend_score": yearly["trend_score"],
            "news_score": news_deep["news_score"],
            "technical_score": tech["technical_bias_score"],
            "intraday_score": intraday["intraday_score"],
            "composite_score": composite,
            "articles_analyzed": news_deep["article_count"],
        },
        "analysis_steps": analysis_steps,
    }

    signal = {
        "signal": signal_label,
        "signal_key": signal_key,
        "confidence_pct": composite,
        "probabilities": {
            "yüksəliş_ehtimalı": bull,
            "eniş_ehtimalı": bear,
            "neytral": neutral,
        },
        "risk_level": risk,
        "reason": _build_signal_reason_simple(signal_key, yearly, news_deep, probabilities),
        "price": price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "atr": price_range["atr"],
        "atr_explanation": (
            f"Stop loss və take profit ATR (${price_range['atr']:.2f}) və "
            f"dəstək/müqavimət səviyyələrinə əsasən hesablanıb."
        ),
        "disclaimer": "Detallı analiz əsasında ehtimal — investisiya məsləhəti deyil.",
    }

    return {
        "daily_forecast": daily_forecast,
        "signal": signal,
        "probabilities": probabilities,
        "yearly_analysis": yearly,
        "intraday_analysis": intraday,
        "news_analysis": news_deep,
        "analysis_steps": analysis_steps,
        "composite_score": composite,
    }
