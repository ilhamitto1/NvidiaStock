# NVDA AI Trading Intelligence — Deployment Guide

Bu sənəd NVIDIA (NVDA) ehtimal əsaslı AI analiz platformasının quraşdırılması üçün addım-addım təlimatdır.

---

## Sistem tələbləri

- **Docker** 24+ və **Docker Compose** v2
- Və ya lokal inkişaf üçün:
  - Python 3.12+
  - Node.js 20+
  - PostgreSQL 16
  - Redis 7

---

## Sürətli başlanğıc (Docker)

```bash
# 1. Layihə qovluğuna keçin
cd FamilNvidia

# 2. News API açarı (optional) — .env faylı yaradın
echo "NEWS_API_KEY=your_key_here" > .env

# 3. Bütün servisləri işə salın
docker compose up --build -d

# 4. Brauzerdə açın
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

---

## Lokal inkişaf (Docker olmadan)

### Backend

```bash
cd backend

# Virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

# .env faylını kopyalayın
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac

# PostgreSQL və Redis işləməlidir
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# .env.local yaradın
copy .env.local.example .env.local

npm run dev
```

Brauzer: http://localhost:3000

---

## Environment dəyişənləri

| Dəyişən | Təsvir | Default |
|---------|--------|---------|
| `DATABASE_URL` | PostgreSQL bağlantısı | `postgresql://nvda:nvda123@localhost:5432/nvda_trading` |
| `REDIS_URL` | Redis cache | `redis://localhost:6379/0` |
| `NEWS_API_KEY` | NewsAPI.org açarı | boş (demo xəbərlər istifadə olunur) |
| `CORS_ORIGINS` | Frontend URL-ləri | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### News API açarı almaq

1. https://newsapi.org qeydiyyatdan keçin
2. Pulsuz plan gündə 100 sorğu verir
3. Açarı `.env` faylına əlavə edin: `NEWS_API_KEY=abc123...`

News API olmadan sistem demo NVIDIA xəbərləri ilə işləyir.

---

## API endpoint-ləri

| Endpoint | Metod | Təsvir |
|----------|-------|--------|
| `/api/health` | GET | Sistem statusu |
| `/api/price` | GET | NVDA qiymət paneli |
| `/api/chart?days=90` | GET | Qrafik məlumatları |
| `/api/technical` | GET | Texniki analiz |
| `/api/news` | GET | Xəbər analizi |
| `/api/sentiment` | GET | AI sentiment |
| `/api/signal` | GET | Siqnal sistemi |
| `/api/backtest/30` | GET | 30 günlük backtest |
| `/api/backtest/90` | GET | 90 günlük backtest |
| `/api/risk` | POST | Risk hesablaması |
| `/api/dashboard?capital=10000` | GET | Tam dashboard |

Swagger docs: http://localhost:8000/docs

---

## Production deployment

### 1. Cloud server (VPS)

```bash
# Serverə SSH
ssh user@your-server

# Layihəni klonlayın
git clone <repo-url> nvda-platform
cd nvda-platform

# Production .env
cat > .env << EOF
NEWS_API_KEY=your_production_key
EOF

# Backend .env
cat > backend/.env << EOF
DATABASE_URL=postgresql://nvda:STRONG_PASSWORD@postgres:5432/nvda_trading
REDIS_URL=redis://redis:6379/0
NEWS_API_KEY=your_production_key
CORS_ORIGINS=https://yourdomain.com
EOF

docker compose up --build -d
```

### 2. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

### 3. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## Arxitektura

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Frontend   │────▶│   Backend   │────▶│ Yahoo Finance│
│  Next.js    │     │   FastAPI   │     └──────────────┘
│  :3000      │     │   :8000     │     ┌──────────────┐
└─────────────┘     └──────┬──────┘────▶│   News API   │
                           │            └──────────────┘
                    ┌──────┴──────┐
                    │             │
               ┌────▼───┐   ┌─────▼────┐
               │ Redis  │   │PostgreSQL│
               │ Cache  │   │   DB     │
               └────────┘   └──────────┘
```

---

## Modullar

| Modul | Fayl | Funksiya |
|-------|------|----------|
| Qiymət paneli | `market_data.py` | Yahoo Finance real-time data |
| Texniki analiz | `technical_analysis.py` | RSI, MACD, EMA, Bollinger, Həcm |
| Xəbər analizi | `news_analysis.py` | News API + sentiment scoring |
| AI Sentiment | `sentiment_analysis.py` | Bullish/Bearish/Risk faktorları |
| Siqnal sistemi | `signal_engine.py` | Ehtimal əsaslı siqnallar |
| Backtest | `backtest.py` | 30/90 günlük tarixi analiz |
| Risk sistemi | `risk_management.py` | Kapital, stop loss, max itki |

---

## Vacib qeydlər

- **Bu investisiya məsləhəti DEYİL.** Bütün nəticələr ehtimal əsaslıdır.
- Backtest nəticələri keçmiş performansı göstərir — gələcək zəmanət deyil.
- Yahoo Finance məlumatları 15 dəqiqə gecikməli ola bilər.
- Production-da PostgreSQL parolunu mütləq dəyişin.

---

## Problemlərin həlli

| Problem | Həll |
|---------|------|
| Backend qoşulmur | `docker compose logs backend` yoxlayın |
| NVDA məlumatı gəlmir | İnternet bağlantısını yoxlayın |
| Xəbərlər boşdur | NEWS_API_KEY əlavə edin və ya demo data istifadə olunur |
| Redis xətası | `docker compose restart redis` |
| CORS xətası | `CORS_ORIGINS`-ə frontend URL əlavə edin |

---

## Dəstək

Platforma haqqında suallar üçün layihə README.md faylına baxın.
