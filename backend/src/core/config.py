from pydantic import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "WhatsApp Bot Backend"
    DEBUG: bool = False

    # Database Settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "whatsapp_bot")
    TEST_DB_NAME: str = os.getenv("TEST_DB_NAME", "test_whatsapp_bot")  # Add this line

    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    API_KEY_NAME: str = "X-API-Key"
    API_KEY: str = os.getenv("API_KEY", "your-api-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"  # Add this line
    VALID_API_KEYS: list = ["test-api-key"]  # Add this line for testing

    # Queue Settings (for future implementation)
    QUEUE_HOST: Optional[str] = None
    QUEUE_PORT: Optional[int] = None
    QUEUE_TYPE: str = "redis"  # or "rabbitmq"

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()