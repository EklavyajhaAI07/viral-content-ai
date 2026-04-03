from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "viral-content-ai"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "changeme"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    POSTGRES_URL: str = ""
    MONGO_URL: str = "mongodb://localhost:27017/viral_content_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    INSTAGRAM_ACCESS_TOKEN: Optional[str] = ""
    YOUTUBE_API_KEY: Optional[str] = ""
    TWITTER_BEARER_TOKEN: Optional[str] = ""
    TIKTOK_API_KEY: Optional[str] = ""

    class Config:
        env_file = ".env"

settings = Settings()
