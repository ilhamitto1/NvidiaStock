from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import api

app = FastAPI(
    title="NVDA AI Trading Intelligence",
    description="NVIDIA (NVDA) ehtimal əsaslı AI analiz platforması",
    version="1.0.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.get("/")
async def root():
    return {
        "platform": "NVDA AI Trading Intelligence",
        "message": "NVIDIA ehtimal əsaslı analiz sistemi",
        "docs": "/docs",
    }
