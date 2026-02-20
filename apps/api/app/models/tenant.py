"""Tenant model — multi-tenancy core."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="starter")
    status: Mapped[str] = mapped_column(String(20), default="active")

    rate_limit_rpm: Mapped[int] = mapped_column(default=60)
    daily_budget_usd: Mapped[float] = mapped_column(Float, default=50.0)
    max_users: Mapped[int] = mapped_column(default=5)

    nexus_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    deepseek_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rag_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    code_studio_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    allowed_models: Mapped[list] = mapped_column(JSON, default=list)
    data_residency_region: Mapped[str] = mapped_column(String(50), default="us-east-1")
    custom_system_prompt: Mapped[str | None] = mapped_column(String(10_000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
