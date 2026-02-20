from dataclasses import dataclass
from datetime import date


@dataclass
class TenantBudget:
    tenant_id: str
    monthly_cap_usd: float
    hard_cap_usd: float
    disabled: bool = False


class CostAnalyticsService:
    """Reference FinOps service for tenant-level budget enforcement."""

    def __init__(self):
        self._budgets: dict[str, TenantBudget] = {}
        self._spend: dict[tuple[str, str], float] = {}

    def set_budget(self, tenant_id: str, monthly_cap_usd: float, hard_cap_usd: float) -> TenantBudget:
        budget = TenantBudget(tenant_id=tenant_id, monthly_cap_usd=monthly_cap_usd, hard_cap_usd=hard_cap_usd)
        self._budgets[tenant_id] = budget
        return budget

    def record_cost(self, tenant_id: str, amount_usd: float, period: str | None = None) -> dict:
        month = period or date.today().strftime("%Y-%m")
        key = (tenant_id, month)
        self._spend[key] = self._spend.get(key, 0.0) + amount_usd

        budget = self._budgets.get(tenant_id)
        if not budget:
            return {"tenant_id": tenant_id, "period": month, "total_usd": self._spend[key], "status": "no_budget"}

        total = self._spend[key]
        if total >= budget.hard_cap_usd:
            budget.disabled = True
            status = "disabled_hard_cap"
        elif total >= budget.monthly_cap_usd:
            status = "cap_reached"
        else:
            status = "within_budget"

        return {
            "tenant_id": tenant_id,
            "period": month,
            "total_usd": round(total, 4),
            "monthly_cap_usd": budget.monthly_cap_usd,
            "hard_cap_usd": budget.hard_cap_usd,
            "disabled": budget.disabled,
            "status": status,
        }

    def get_cost_summary(self, period: str | None = None) -> dict:
        month = period or date.today().strftime("%Y-%m")
        rows = [
            {"tenant_id": tenant, "period": p, "cost_usd": cost}
            for (tenant, p), cost in self._spend.items()
            if p == month
        ]
        return {
            "period": month,
            "cost_per_tenant": sorted(rows, key=lambda r: r["cost_usd"], reverse=True),
            "cost_per_model": [],
            "cost_per_endpoint": [],
            "cost_per_feature": [],
        }
