import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.config import settings
from app.services.translation import translate_article
from app.redis_client import cache_get, cache_set

NVIDIA_KEYWORDS = [
    "NVIDIA", "NVDA", "AI chip", "GPU", "data center",
    "supercomputer", "H100", "Blackwell", "CUDA", "Jensen Huang",
]

DEMO_NEWS = [
    {
        "title": "NVIDIA yeni AI çip nəsilini təqdim etdi — data center performansı 2x artdı",
        "source": "TechNews AZ",
        "url": "#",
        "published_at": "2025-06-22T10:00:00",
        "category": "AI çip xəbərləri",
        "sentiment": "müsbət",
        "impact_strength": 85,
        "summary": "Yeni çip nəsilinin data center satışlarına güclü təsir göstərməsi gözlənilir.",
    },
    {
        "title": "Böyük bulud provayderləri NVIDIA GPU sifarişlərini artırdı",
        "source": "MarketWatch",
        "url": "#",
        "published_at": "2025-06-21T14:30:00",
        "category": "GPU satış xəbərləri",
        "sentiment": "müsbət",
        "impact_strength": 78,
        "summary": "Microsoft, Google və Amazon yeni GPU partiyaları sifariş etdi.",
    },
    {
        "title": "ABŞ Çinə NVIDIA çip ixracına yeni məhdudiyyətlər qoydu",
        "source": "Reuters",
        "url": "#",
        "published_at": "2025-06-20T09:15:00",
        "category": "AI çip xəbərləri",
        "sentiment": "mənfi",
        "impact_strength": 72,
        "summary": "Çin bazarının itirilməsi qısamüddətli gəlirə təsir edə bilər.",
    },
    {
        "title": "NVIDIA supercomputer layihəsində yeni rekord — 10 exaflop güc",
        "source": "HPC World",
        "url": "#",
        "published_at": "2025-06-19T16:00:00",
        "category": "Supercomputer layihələri",
        "sentiment": "müsbət",
        "impact_strength": 70,
        "summary": "Elmi hesablamalar bazarında NVIDIA liderliyini möhkəmləndirir.",
    },
    {
        "title": "Data center gəlirləri analitik proqnozları aşdı",
        "source": "Bloomberg",
        "url": "#",
        "published_at": "2025-06-18T11:45:00",
        "category": "Data center inkişafı",
        "sentiment": "müsbət",
        "impact_strength": 82,
        "summary": "Data center seqmenti NVIDIA-nın əsas gəlir mənbəyinə çevrildi.",
    },
    {
        "title": "Rəqib AMD yeni AI çipini erkən buraxdı — bazar payı mübarizəsi güclənir",
        "source": "CNBC",
        "url": "#",
        "published_at": "2025-06-17T08:20:00",
        "category": "AI çip xəbərləri",
        "sentiment": "mənfi",
        "impact_strength": 55,
        "summary": "Rəqabət artması qısamüddətli qiymət təzyiqinə səbəb ola bilər.",
    },
    {
        "title": "NVIDIA avtomobil AI platformasını genişləndirdi",
        "source": "Automotive News",
        "url": "#",
        "published_at": "2025-06-16T13:00:00",
        "category": "GPU satış xəbərləri",
        "sentiment": "müsbət",
        "impact_strength": 60,
        "summary": "Avtonom sürücülük bazarı yeni gəlir mənbəyi yarada bilər.",
    },
    {
        "title": "FED faiz qərarı bazar volatilliyini artırdı — texnologiya səhmləri təzyiq altında",
        "source": "Financial Times",
        "url": "#",
        "published_at": "2025-06-15T17:30:00",
        "category": "Data center inkişafı",
        "sentiment": "mənfi",
        "impact_strength": 45,
        "summary": "Ümumi bazar riski NVDA-ya da təsir edir, birbaşa NVIDIA xəbəri deyil.",
    },
]


def _classify_article(title: str, description: str) -> tuple[str, str, int]:
    text = (title + " " + description).lower()
    positive_words = ["surge", "record", "growth", "beat", "demand", "partnership", "launch", "strong", "rise"]
    negative_words = ["ban", "restrict", "decline", "miss", "competition", "lawsuit", "cut", "fall", "risk"]

    pos = sum(1 for w in positive_words if w in text)
    neg = sum(1 for w in negative_words if w in text)

    if "data center" in text or "datacenter" in text:
        category = "Data center inkişafı"
    elif "supercomputer" in text or "exaflop" in text:
        category = "Supercomputer layihələri"
    elif "gpu" in text or "sales" in text:
        category = "GPU satış xəbərləri"
    else:
        category = "AI çip xəbərləri"

    if pos > neg:
        sentiment = "müsbət"
        strength = min(100, 50 + pos * 15)
    elif neg > pos:
        sentiment = "mənfi"
        strength = min(100, 50 + neg * 15)
    else:
        sentiment = "neytral"
        strength = 40

    return sentiment, category, strength


async def _process_article(item: dict) -> dict[str, Any]:
    title_en = item.get("title", "")
    summary_en = (item.get("description") or "")[:200]
    title_az, summary_az = await asyncio.to_thread(translate_article, title_en, summary_en)
    sentiment, category, strength = _classify_article(title_en, summary_en)
    return {
        "title": title_az,
        "title_original": title_en,
        "source": item.get("source", {}).get("name", "Unknown"),
        "url": item.get("url", "#"),
        "published_at": item.get("publishedAt", datetime.utcnow().isoformat()),
        "category": category,
        "sentiment": sentiment,
        "impact_strength": strength,
        "summary": summary_az,
        "summary_original": summary_en,
        "translated": True,
    }


async def fetch_news() -> list[dict[str, Any]]:
    cache_key = "nvda_news_az_v1"
    cached = cache_get(cache_key)
    if cached:
        return cached

    articles: list[dict[str, Any]] = []

    if settings.news_api_key:
        try:
            query = "NVIDIA OR NVDA"
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 15,
                "apiKey": settings.news_api_key,
            }
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_articles = data.get("articles", [])[:12]
                    articles = list(await asyncio.gather(
                        *[_process_article(item) for item in raw_articles]
                    ))
        except Exception:
            pass

    if not articles:
        articles = DEMO_NEWS

    cache_set(cache_key, articles, ttl=600)
    return articles


def analyze_news(news: list[dict[str, Any]]) -> dict[str, Any]:
    positive = [n for n in news if n["sentiment"] == "müsbət"]
    negative = [n for n in news if n["sentiment"] == "mənfi"]

    pos_strength = sum(n["impact_strength"] for n in positive) / len(positive) if positive else 0
    neg_strength = sum(n["impact_strength"] for n in negative) / len(negative) if negative else 0

    total = pos_strength + neg_strength
    if total > 0:
        bullish_pct = round(pos_strength / total * 100, 1)
        bearish_pct = round(neg_strength / total * 100, 1)
    else:
        bullish_pct, bearish_pct = 50.0, 50.0

    neutral_pct = round(max(0, 100 - bullish_pct - bearish_pct), 1)

    return {
        "total_articles": len(news),
        "positive_count": len(positive),
        "negative_count": len(negative),
        "news_bias_score": round(bullish_pct, 1),
        "summary": {
            "yüksəliş_ehtimalı": bullish_pct,
            "eniş_ehtimalı": bearish_pct,
            "neytral": neutral_pct,
        },
    }
