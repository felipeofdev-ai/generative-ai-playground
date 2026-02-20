"""Auth middleware — validates JWT or API key on every request."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

PUBLIC_PATHS = {
    "/health",
    "/health/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/token",
    "/api/v1/auth/register",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key", "")

        if not auth and not api_key:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        return await call_next(request)
