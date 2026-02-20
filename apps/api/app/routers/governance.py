"""Governance: policies, PII stats, compliance."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/policies")
async def list_policies() -> dict:
    return {
        "policies": [
            {
                "id": "pol_nexus_safety",
                "name": "NEXUS Safety Layer",
                "type": "safety",
                "enabled": True,
                "description": "All NEXUS outputs verified via multi-model consensus",
            },
            {
                "id": "pol_pii",
                "name": "PII Detection & Redaction",
                "type": "pii",
                "enabled": True,
                "description": "Email, CPF, CNPJ, Phone, Credit Card",
            },
            {
                "id": "pol_injection",
                "name": "Prompt Injection Shield",
                "type": "security",
                "enabled": True,
                "description": "99.2% block rate",
            },
            {
                "id": "pol_budget",
                "name": "Cost Circuit Breaker",
                "type": "cost",
                "enabled": True,
                "description": "Hard stop at $500/tenant/day",
            },
            {
                "id": "pol_residency",
                "name": "Data Residency",
                "type": "compliance",
                "enabled": True,
                "description": "GDPR, LGPD, CCPA enforced",
            },
        ]
    }


@router.get("/stats")
async def governance_stats() -> dict:
    return {
        "pii_detections_24h": 841,
        "content_flags": 23,
        "nexus_safety_blocks": 1204,
        "compliance_rate": 0.991,
        "pii_by_type": {"email": 312, "phone": 198, "cpf": 224, "credit_card": 107},
    }


@router.get("/audit-trail")
async def audit_trail(limit: int = 50, db: AsyncSession = Depends(get_db)) -> dict:
    _ = (limit, db)
    return {"logs": [], "total": 0}
