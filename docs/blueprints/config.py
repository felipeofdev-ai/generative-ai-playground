from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "NexusAI Platform"
    app_version: str = "1.0.0"
    database_url: str = Field(default="postgresql+asyncpg://nexusai:nexusai@localhost:5432/nexusai")
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = Field(min_length=32)
    openai_api_key: str = ""

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
