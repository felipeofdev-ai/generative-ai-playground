from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.config import settings

app = FastAPI(
    title="NexusAI Platform API",
    version=settings.app_version,
    default_response_class=ORJSONResponse,
)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}
