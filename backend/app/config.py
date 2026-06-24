import os

from pydantic_settings import BaseSettings


def _default_cors() -> str:
    origins = ["http://localhost:3000"]
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        origins.append(f"https://{vercel_url}")
    return ",".join(origins)


class Settings(BaseSettings):
    database_url: str = "postgresql://nvda:nvda123@localhost:5432/nvda_trading"
    redis_url: str = "redis://localhost:6379/0"
    news_api_key: str = ""
    cors_origins: str = _default_cors()
    cache_ttl_seconds: int = 300
    symbol: str = "NVDA"

    class Config:
        env_file = ".env"


settings = Settings()
