import importlib.util
from pathlib import Path


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_budget_enforcement_hard_cap():
    mod = load_module("cost-analytics/cost_api.py", "cost_api")
    svc = mod.CostAnalyticsService()
    svc.set_budget("t1", monthly_cap_usd=100.0, hard_cap_usd=120.0)
    r1 = svc.record_cost("t1", 60.0, period="2026-01")
    r2 = svc.record_cost("t1", 70.0, period="2026-01")
    assert r1["status"] == "within_budget"
    assert r2["status"] == "disabled_hard_cap"
    assert r2["disabled"] is True


def test_policy_engine_rules():
    mod = load_module("policy-engine/policy_engine.py", "policy_engine")
    eng = mod.PolicyEngine()
    deny = eng.enforce_request(tenant_plan="enterprise", model="unknown-model", prompt="hello", tokens=100)
    assert deny.allowed is False
    deny2 = eng.enforce_request(tenant_plan="enterprise", model="gpt-4o", prompt="illegal activity", tokens=100)
    assert deny2.allowed is False
