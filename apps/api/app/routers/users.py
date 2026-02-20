"""User management CRUD + RBAC."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.routers.auth import hash_password

router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "viewer"
    password: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


@router.get("/")
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _auth: Annotated[bool, Depends(require_role(["admin", "developer"]))],
    tenant_id: str = "",
) -> dict:
    result = await db.execute(select(User).where(User.tenant_id == tenant_id, User.is_active.is_(True)))
    users = result.scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.full_name,
                "role": u.role,
                "last_active_at": u.last_active_at,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "total": len(users),
    }


@router.post("/invite", status_code=201)
async def invite_user(req: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    user = User(
        tenant_id="",
        email=req.email,
        full_name=req.full_name,
        role=req.role,
        hashed_password=hash_password(req.password) if req.password else None,
    )
    db.add(user)
    await db.commit()
    return {"id": user.id, "email": user.email, "message": "Invitation sent"}


@router.patch("/{user_id}")
async def update_user(user_id: str, req: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    await db.commit()
    return {"id": user.id, "updated": True}


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
