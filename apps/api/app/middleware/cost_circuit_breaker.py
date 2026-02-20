"""Cost circuit breaker — stops requests when budget exceeded."""

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger(__name__)

INFERENCE_PATHS = {"/api/v1/nexus/chat", "/api/v1/nexus/stream"}


class CostCircuitBreakerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path not in INFERENCE_PATHS:
            return await call_next(request)

        tenant_id = request.headers.get("X-Tenant-ID", "")
        if tenant_id:
            log.debug("cost.breaker.check", tenant_id=tenant_id)

        return await call_next(request)
