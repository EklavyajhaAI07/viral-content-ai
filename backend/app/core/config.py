from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # ─── App ──────────────────────────────────────────
    APP_NAME: str = "Viral Content AI"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ─── JWT Auth ─────────────────────────────────────
    SECRET_KEY: str = "super-secret-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ─── Database ─────────────────────────────────────
    POSTGRES_URL: str = "postgresql://postgres:password@localhost:5432/viral_content_db"
    MONGO_URL: str = "mongodb://localhost:27017/viral_content_db"

    # ─── Cache / Queue ────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── AI / LLM ─────────────────────────────────────
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: Optional[str] = ""
    ANTHROPIC_API_KEY: Optional[str] = ""

    # ─── Social / Trend APIs ──────────────────────────
    SERPAPI_KEY: Optional[str] = ""
    YOUTUBE_API_KEY: Optional[str] = ""
    TWITTER_BEARER_TOKEN: Optional[str] = ""
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = ""
    TIKTOK_API_KEY: Optional[str] = ""

    # ─── CORS ─────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # ─── Rate Limiting ────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 20

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
