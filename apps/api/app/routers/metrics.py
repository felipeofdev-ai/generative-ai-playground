"""Prometheus metrics + platform stats."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics() -> str:
    return """
# HELP nexusai_inferences_total Total inference requests
# TYPE nexusai_inferences_total counter
nexusai_inferences_total{model="gpt-4o",provider="openai"} 2841022
nexusai_inferences_total{model="deepseek-r1",provider="deepseek"} 782410

# HELP nexusai_latency_ms Inference latency in milliseconds
# TYPE nexusai_latency_ms histogram
nexusai_latency_ms_bucket{model="gpt-4o",le="100"} 12000
nexusai_latency_ms_bucket{model="gpt-4o",le="500"} 89000
nexusai_latency_ms_bucket{model="gpt-4o",le="+Inf"} 92000

# HELP nexusai_cost_usd_total Total cost in USD
# TYPE nexusai_cost_usd_total counter
nexusai_cost_usd_total{tenant="acme"} 24100.0
"""


@router.get("/platform")
async def platform_stats() -> dict:
    return {
        "inferences_today": 4_820_000,
        "nexus_tasks_resolved": 18_400,
        "avg_latency_ms": 198,
        "monthly_cost_usd": 24100,
        "providers_online": 6,
        "sla_uptime_30d": 0.9997,
    }
