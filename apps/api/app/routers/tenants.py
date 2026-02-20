"""Tenant management."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tenant import Tenant

router = APIRouter()


class TenantUpdate(BaseModel):
    name: str | None = None
    plan: str | None = None
    daily_budget_usd: float | None = None
    nexus_enabled: bool | None = None


@router.get("/")
async def list_tenants(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Tenant).where(Tenant.status == "active"))
    tenants = result.scalars().all()
    return {"tenants": [{"id": t.id, "name": t.name, "plan": t.plan, "status": t.status} for t in tenants]}


@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "id": tenant.id,
        "name": tenant.name,
        "plan": tenant.plan,
        "nexus_enabled": tenant.nexus_enabled,
        "rate_limit_rpm": tenant.rate_limit_rpm,
    }


@router.patch("/{tenant_id}")
async def update_tenant(tenant_id: str, req: TenantUpdate, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if req.name is not None:
        tenant.name = req.name
    if req.plan is not None:
        tenant.plan = req.plan
    if req.daily_budget_usd is not None:
        tenant.daily_budget_usd = req.daily_budget_usd
    if req.nexus_enabled is not None:
        tenant.nexus_enabled = req.nexus_enabled
    await db.commit()
    return {"id": tenant.id, "updated": True}
