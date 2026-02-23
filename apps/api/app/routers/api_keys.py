"""API Key management."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_tenant, get_current_user
from app.models.api_key import APIKey

router = APIRouter()


class CreateKeyRequest(BaseModel):
    name: str
    permissions: list[str] = ["nexus:read", "nexus:write"]
    allowed_models: list[str] = []
    rate_limit_rpm: int = 60
    expires_in_days: int | None = None


@router.get("/")
async def list_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> dict:
    result = await db.execute(
        select(APIKey).where(APIKey.is_active.is_(True), APIKey.tenant_id == tenant["id"])
    )
    keys = result.scalars().all()
    return {
        "keys": [
            {
                "id": k.id,
                "name": k.name,
                "key_prefix": k.key_prefix,
                "permissions": k.permissions,
                "rate_limit_rpm": k.rate_limit_rpm,
                "last_used_at": k.last_used_at,
                "created_at": k.created_at,
                "expires_at": k.expires_at,
            }
            for k in keys
        ]
    }


@router.post("/", status_code=201)
async def create_key(
    req: CreateKeyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    raw_key, hashed = APIKey.generate()
    key = APIKey(
        tenant_id=tenant["id"],
        created_by=user["id"],
        name=req.name,
        key_hash=hashed,
        key_prefix=raw_key[:20],
        permissions=req.permissions,
        allowed_models=req.allowed_models,
        rate_limit_rpm=req.rate_limit_rpm,
        expires_at=(
            datetime.now(timezone.utc) + timedelta(days=req.expires_in_days)
            if req.expires_in_days
            else None
        ),
    )
    db.add(key)
    await db.commit()
    return {
        "id": key.id,
        "key": raw_key,
        "name": key.name,
        "message": "Save this key securely — it will not be shown again",
    }


@router.delete("/{key_id}", status_code=204)
async def revoke_key(
    key_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> None:
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.tenant_id == tenant["id"])
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.is_active = False
    await db.commit()