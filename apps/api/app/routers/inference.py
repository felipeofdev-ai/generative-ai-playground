"""Inference logs endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.inference_log import InferenceLog

router = APIRouter()


@router.get("/logs")
async def get_logs(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    model: str | None = None,
) -> dict:
    query = select(InferenceLog).order_by(desc(InferenceLog.created_at)).limit(limit).offset((page - 1) * limit)
    if model:
        query = query.where(InferenceLog.model == model)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": l.id,
                "request_id": l.request_id,
                "model": l.model,
                "latency_ms": l.latency_ms,
                "cost_usd": l.cost_usd,
                "total_tokens": l.total_tokens,
                "safety_passed": l.safety_passed,
                "created_at": l.created_at,
            }
            for l in logs
        ],
        "page": page,
        "limit": limit,
    }
