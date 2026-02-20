"""FastAPI dependencies — auth, tenant context, service injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.api_key import APIKey
from app.models.tenant import Tenant
from app.models.user import User
from app.services.nexus_orchestrator import NexusOrchestrator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_nexus_instance: NexusOrchestrator | None = None


def get_nexus() -> NexusOrchestrator:
    global _nexus_instance
    if _nexus_instance is None:
        _nexus_instance = NexusOrchestrator()
    return _nexus_instance


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub", "")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"id": user.id, "email": user.email, "role": user.role, "tenant_id": user.tenant_id}


async def get_current_tenant(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    tenant_id = request.headers.get("X-Tenant-ID") or getattr(request.state, "tenant_id", "")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id, Tenant.status == "active"))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "id": tenant.id,
        "name": tenant.name,
        "plan": tenant.plan,
        "nexus_enabled": tenant.nexus_enabled,
        "daily_budget_usd": tenant.daily_budget_usd,
    }


async def get_api_key_context(
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict | None:
    if not api_key:
        return None
    key_hash = APIKey.hash(api_key)
    result = await db.execute(select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active.is_(True)))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return {"id": key.id, "tenant_id": key.tenant_id, "permissions": key.permissions, "rate_limit_rpm": key.rate_limit_rpm}


def require_role(*roles: str):
    async def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail=f"Role '{user['role']}' not permitted. Required: {roles}")
        return user

    return checker
