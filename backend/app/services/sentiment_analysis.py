from typing import Any

from app.services.news_analysis import analyze_news, fetch_news


async def get_sentiment_analysis() -> dict[str, Any]:
    news = await fetch_news()
    news_stats = analyze_news(news)

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
                "explanation": f"Bu xəbər NVDA üçün müsbət siqnaldır (güc: {article['impact_strength']}/100).",
            })
        elif article["sentiment"] == "mənfi" and article["impact_strength"] >= 50:
            bearish_factors.append({
                **factor,
                "explanation": f"Bu xəbər NVDA üçün mənfi təsir yarada bilər (güc: {article['impact_strength']}/100).",
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

    overall = news_stats["summary"]
    sentiment_score = news_stats["news_bias_score"]

    if sentiment_score >= 65:
        mood = "Optimist"
        mood_az = "Xəbər axını ümumilikdə müsbətdir — investorlar NVIDIA-ya inam göstərir."
    elif sentiment_score <= 35:
        mood = "Pessimist"
        mood_az = "Xəbər axını mənfi cəhətdən yüklənib — ehtiyatlı olmaq lazımdır."
    else:
        mood = "Qarışıq"
        mood_az = "Xəbərlər qarışıqdır — aydın istiqamət siqnalı yoxdur."

    return {
        "mood": mood,
        "mood_explanation": mood_az,
        "probabilities": overall,
        "sentiment_score": sentiment_score,
        "bullish_factors": bullish_factors[:5],
        "bearish_factors": bearish_factors[:5],
        "risk_factors": risk_factors[:5],
        "disclaimer": "Bu sentiment analizi ehtimal əsaslıdır, gələcək qiymət zəmanəti deyil.",
    }
