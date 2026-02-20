"""Inference log — every API call recorded."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InferenceLog(Base):
    __tablename__ = "inference_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    api_key_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    pipeline_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    model: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    mode: Mapped[str] = mapped_column(String(50), default="chat")

    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    consensus_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    synthesized: Mapped[bool] = mapped_column(Boolean, default=False)
    models_used: Mapped[list] = mapped_column(JSON, default=list)

    safety_passed: Mapped[bool] = mapped_column(Boolean, default=True)
    pii_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    pii_entities: Mapped[list] = mapped_column(JSON, default=list)

    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status_code: Mapped[int] = mapped_column(Integer, default=200)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
