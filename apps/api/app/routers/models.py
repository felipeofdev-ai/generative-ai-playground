"""Model registry and benchmarks."""

from fastapi import APIRouter, HTTPException

router = APIRouter()

MODELS = [
    {
        "id": "nexus-ultra",
        "display_name": "NEXUS Ultra",
        "provider": "nexusai",
        "mmlu": 0.994,
        "avg_latency_ms": 42,
        "cost_per_1m_input": 0,
        "status": "online",
    },
    {
        "id": "gpt-4o",
        "display_name": "GPT-4o",
        "provider": "openai",
        "mmlu": 0.872,
        "avg_latency_ms": 218,
        "cost_per_1m_input": 2.50,
        "status": "online",
    },
    {
        "id": "claude-3-5-sonnet-20241022",
        "display_name": "Claude 3.5 Sonnet",
        "provider": "anthropic",
        "mmlu": 0.887,
        "avg_latency_ms": 305,
        "cost_per_1m_input": 3.00,
        "status": "online",
    },
    {
        "id": "deepseek-reasoner",
        "display_name": "DeepSeek-R1",
        "provider": "deepseek",
        "mmlu": 0.908,
        "avg_latency_ms": 280,
        "cost_per_1m_input": 0.55,
        "status": "online",
    },
    {
        "id": "gemini-1.5-pro",
        "display_name": "Gemini 1.5 Pro",
        "provider": "google",
        "mmlu": 0.859,
        "avg_latency_ms": 449,
        "cost_per_1m_input": 7.00,
        "status": "degraded",
    },
    {
        "id": "llama-3.3-70b",
        "display_name": "Llama 3.3 70B",
        "provider": "meta",
        "mmlu": 0.802,
        "avg_latency_ms": 89,
        "cost_per_1m_input": 0.90,
        "status": "online",
    },
]


@router.get("/")
async def list_models() -> dict:
    return {"models": MODELS, "total": len(MODELS)}


@router.get("/{model_id}")
async def get_model(model_id: str) -> dict:
    model = next((m for m in MODELS if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.get("/benchmark/compare")
async def compare_models(model_ids: str = "") -> dict:
    ids = model_ids.split(",") if model_ids else []
    return {"comparison": [m for m in MODELS if m["id"] in ids], "benchmarks": {}}
