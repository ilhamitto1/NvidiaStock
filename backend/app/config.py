from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://nvda:nvda123@localhost:5432/nvda_trading"
    redis_url: str = "redis://localhost:6379/0"
    news_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    cache_ttl_seconds: int = 300
    symbol: str = "NVDA"

    class Config:
        env_file = ".env"


settings = Settings()
