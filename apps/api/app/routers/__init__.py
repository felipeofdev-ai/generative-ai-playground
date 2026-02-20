"""
NexusAI — Router registry
Import all routers here so main.py can reference them cleanly.
"""
from app.routers import (
    auth,
    users,
    api_keys,
    pipelines,
    knowledge_base,
    governance,
    costs,
    metrics,
    tenants,
    inference,
    models,
    webhooks,
    nexus,
)

__all__ = [
    "auth",
    "users",
    "api_keys",
    "pipelines",
    "knowledge_base",
    "governance",
    "costs",
    "metrics",
    "tenants",
    "inference",
    "models",
    "webhooks",
    "nexus",
]
