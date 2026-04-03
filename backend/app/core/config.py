from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json

class Settings(BaseSettings):
    # App
    APP_NAME: str = "viral-content-ai"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    POSTGRES_URL: str
    MONGO_URL: str

    # AI / LLM
    GROQ_API_KEY: str
    OPENROUTER_API_KEY: str
    
    # Trend APIs
    SERPAPI_KEY: str
    YOUTUBE_API_KEY: str

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()