"""
NexusAI — FastAPI main application
Tier 1 Enterprise AI Orchestration Platform
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.cache import check_redis_health
from app.config import settings
from app.database import check_db_health, create_tables
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.cost_circuit_breaker import CostCircuitBreakerMiddleware
from app.middleware.tenant_middleware import TenantMiddleware
from app.routers import (
    api_keys,
    auth,
    costs,
    governance,
    inference,
    knowledge_base,
    metrics,
    models,
    nexus,
    pipelines,
    tenants,
    users,
    webhooks,
)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    log.info("nexusai.startup", env=settings.environment, version="3.0.0")
    await create_tables()
    yield
    log.info("nexusai.shutdown")


app = FastAPI(
    title="NexusAI API",
    description="World's Most Advanced Enterprise GenAI Orchestration Platform",
    version="3.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Tenant-ID", "X-Cost-USD", "X-Latency-MS"],
)
app.add_middleware(CostCircuitBreakerMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)


@app.middleware("http")
async def add_timing_headers(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    elapsed = (time.monotonic() - start) * 1000
    response.headers["X-Latency-MS"] = f"{elapsed:.2f}"
    return response


PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{PREFIX}/auth", tags=["Auth"])
app.include_router(nexus.router, prefix=f"{PREFIX}/nexus", tags=["NEXUS"])
app.include_router(users.router, prefix=f"{PREFIX}/users", tags=["Users"])
app.include_router(api_keys.router, prefix=f"{PREFIX}/api-keys", tags=["API Keys"])
app.include_router(tenants.router, prefix=f"{PREFIX}/tenants", tags=["Tenants"])
app.include_router(pipelines.router, prefix=f"{PREFIX}/pipelines", tags=["Pipelines"])
app.include_router(knowledge_base.router, prefix=f"{PREFIX}/knowledge-base", tags=["Knowledge Base"])
app.include_router(governance.router, prefix=f"{PREFIX}/governance", tags=["Governance"])
app.include_router(costs.router, prefix=f"{PREFIX}/costs", tags=["Costs"])
app.include_router(metrics.router, prefix=f"{PREFIX}/metrics", tags=["Metrics"])
app.include_router(inference.router, prefix=f"{PREFIX}/inference", tags=["Inference"])
app.include_router(models.router, prefix=f"{PREFIX}/models", tags=["Models"])
app.include_router(webhooks.router, prefix=f"{PREFIX}/webhooks", tags=["Webhooks"])


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok", "version": "3.0.0", "service": "nexusai-api"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    ok = db_ok and redis_ok
    return JSONResponse(
        status_code=200 if ok else 503,
        content={
            "status": "ready" if ok else "degraded",
            "checks": {"database": db_ok, "redis": redis_ok},
        },
    )


@app.get("/health/live", tags=["Health"])
async def liveness() -> dict:
    return {"status": "alive"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
