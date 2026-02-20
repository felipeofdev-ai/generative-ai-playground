"""Cost analytics endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
async def cost_summary() -> dict:
    return {
        "mtd_spend_usd": 24100.0,
        "projected_eom_usd": 31400.0,
        "budget_usd": 30000.0,
        "saved_by_nexus_usd": 8400.0,
        "cost_per_1m_tokens": 4.82,
        "by_model": [
            {"model": "gpt-4o", "cost_usd": 10800, "pct": 0.45},
            {"model": "claude-3-5-sonnet", "cost_usd": 4800, "pct": 0.20},
            {"model": "deepseek-r1", "cost_usd": 1900, "pct": 0.08},
            {"model": "others", "cost_usd": 6600, "pct": 0.27},
        ],
        "daily": [{"date": "2025-02-01", "actual_usd": 820.0, "projected_usd": None}],
    }


@router.get("/by-tenant")
async def costs_by_tenant() -> dict:
    return {"tenants": []}


@router.get("/budget-alerts")
async def budget_alerts() -> dict:
    return {"alerts": [{"tenant": "Acme Corp", "pct_used": 0.87, "spend_usd": 24100}]}
