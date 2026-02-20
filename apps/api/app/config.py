"""Minimal NexusAI settings for API modules."""

from dataclasses import dataclass
import os


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://nexusai:nexusai@localhost:5432/nexusai")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    jwt_secret: str = os.getenv("JWT_SECRET", "dev_secret_change_me_32_chars_minimum")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    environment: str = os.getenv("ENVIRONMENT", "development")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()
