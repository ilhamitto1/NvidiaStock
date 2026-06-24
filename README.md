# NVDA AI Trading Intelligence

NVIDIA (NVDA) üçün ehtimal əsaslı AI analiz platforması — tamamilə Azərbaycan dilində.

## Xüsusiyyətlər

- **Qiymət paneli** — Real vaxt NVDA qiyməti, gündəlik/həftəlik dəyişmə
- **Texniki analiz** — RSI, MACD, EMA, Bollinger Bands, Həcm (sadə izahlarla)
- **Xəbər analizi** — AI çip, data center, supercomputer, GPU xəbərləri
- **AI Sentiment** — Bullish/Bearish/Risk faktorları
- **Siqnal sistemi** — Ehtimal faizləri ilə (heç vaxt "qalxacaq" demir!)
- **Backtest** — 30/90 günlük tarixi analiz
- **Risk sistemi** — Kapitala görə investisiya tövsiyəsi

## Texnologiyalar

| Qat | Texnologiya |
|-----|-------------|
| Frontend | Next.js, TypeScript, TailwindCSS, Recharts |
| Backend | FastAPI, Python |
| Database | PostgreSQL |
| Cache | Redis |
| Data | Yahoo Finance, News API |

## Sürətli başlanğıc

```bash
# Docker ilə (tövsiyə olunur)
docker compose up --build -d

# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

Ətraflı quraşdırma: [DEPLOYMENT.md](./DEPLOYMENT.md)

## Layihə strukturu

```
FamilNvidia/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Konfiqurasiya
│   │   ├── routers/api.py       # API endpoint-ləri
│   │   └── services/
│   │       ├── market_data.py       # Yahoo Finance
│   │       ├── technical_analysis.py # RSI, MACD, EMA...
│   │       ├── news_analysis.py     # Xəbər analizi
│   │       ├── sentiment_analysis.py # AI sentiment
│   │       ├── signal_engine.py     # Siqnal sistemi
│   │       ├── backtest.py          # Backtest
│   │       └── risk_management.py   # Risk hesablaması
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # UI komponentləri
│   │   └── lib/                 # API client, types
│   └── Dockerfile
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## Əsas prinsip

```
❌ "NVDA qalxacaq"
✔ "Yüksəliş ehtimalı: 68%"
✔ "Eniş ehtimalı: 20%"
✔ "Neytral: 12%"
```

## Disclaimer

Bu platforma investisiya məsləhəti vermir. Bütün analizlər ehtimal əsaslıdır və gələcək qiymət hərəkətini zəmanət etmir.
