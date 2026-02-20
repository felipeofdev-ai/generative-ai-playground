"""
NexusAI — Configuration & Settings
All environment variables with sensible defaults for development.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "dev-secret-change-in-production-please"

    database_url: str = "postgresql+asyncpg://nexusai:nexusai@localhost:5432/nexusai"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "nexusai-jwt-secret-change-this-in-production-32chars+"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 30

    master_encryption_key: str = "0" * 64

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    google_api_key: str = ""
    cohere_api_key: str = ""
    groq_api_key: str = ""
    mistral_api_key: str = ""

    nexus_consensus_threshold: float = 0.75
    nexus_max_models: int = 5
    nexus_timeout_seconds: int = 120
    nexus_cache_ttl: int = 3600

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "nexusai-documents"

    cors_origins: list[str] = ["http://localhost:3000", "https://app.nexusai.com"]

    sentry_dsn: str = ""
    datadog_api_key: str = ""
    otel_endpoint: str = ""

    smtp_host: str = "smtp.sendgrid.net"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@nexusai.com"

    slack_webhook_url: str = ""
    slack_alert_channel: str = "#nexusai-alerts"

    global_daily_budget_usd: float = 10_000.0
    cost_alert_threshold_pct: float = 0.80

    enable_rag: bool = True
    enable_code_studio: bool = True
    enable_webhooks: bool = True
    enable_audit_chain: bool = True
    enable_pii_detection: bool = True

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
