"""NexusAI API application entrypoint."""

from fastapi import FastAPI

from app.routers import (
    api_keys,
    auth,
    costs,
    governance,
    inference,
    knowledge_base,
    metrics,
    models,
    pipelines,
    tenants,
    users,
    webhooks,
)

app = FastAPI(title="NexusAI API", version="1.0.0")

prefix = "/api/v1"
app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{prefix}/users", tags=["Users"])
app.include_router(api_keys.router, prefix=f"{prefix}/api-keys", tags=["API Keys"])
app.include_router(pipelines.router, prefix=f"{prefix}/pipelines", tags=["Pipelines"])
app.include_router(knowledge_base.router, prefix=f"{prefix}/kb", tags=["Knowledge Base"])
app.include_router(governance.router, prefix=f"{prefix}/governance", tags=["Governance"])
app.include_router(costs.router, prefix=f"{prefix}/costs", tags=["Costs"])
app.include_router(metrics.router, prefix=f"{prefix}/metrics", tags=["Metrics"])
app.include_router(tenants.router, prefix=f"{prefix}/tenants", tags=["Tenants"])
app.include_router(inference.router, prefix=f"{prefix}/inference", tags=["Inference"])
app.include_router(models.router, prefix=f"{prefix}/models", tags=["Models"])
app.include_router(webhooks.router, prefix=f"{prefix}/webhooks", tags=["Webhooks"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "nexusai-api"}
