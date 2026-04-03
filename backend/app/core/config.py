from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Viral Content AI"
    DEBUG: bool = False

    # JWT
    SECRET_KEY: str = "super-secret-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 20

    model_config = {
        "env_file": ".env",
        "extra": "ignore",        # ← ignore unknown env vars like GROQ_API_KEY
    }


settings = Settings()
