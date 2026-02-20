"""
NexusAI — NEXUS Router
Core inference endpoints: chat, stream, multi-model comparison.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.dependencies import get_current_tenant, get_nexus
from app.services.nexus_orchestrator import NexusMode, NexusOrchestrator

router = APIRouter()


class Message(BaseModel):
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    mode: NexusMode = NexusMode.CHAT
    model_override: list[str] | None = None
    max_models: int = Field(default=3, ge=1, le=5)
    system_prompt: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32768)
    stream: bool = False


class ChatResponse(BaseModel):
    request_id: str
    response: str
    mode: str
    models_used: list[dict]
    consensus_score: float
    latency_ms: float
    cost_usd: float
    synthesized: bool
    safety_passed: bool
    pii_detected: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    request: Request,
    nexus: Annotated[NexusOrchestrator, Depends(get_nexus)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> ChatResponse:
    if not tenant.get("nexus_enabled", True):
        raise HTTPException(status_code=403, detail="NEXUS not enabled for this tenant")

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user:
        raise HTTPException(status_code=422, detail="No user message found")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    result = await nexus.orchestrate(
        prompt=last_user.content,
        mode=req.mode,
        tenant_id=tenant["id"],
        user_id=request.state.__dict__.get("user_id", ""),
        messages=messages,
        override_models=req.model_override,
        max_models=req.max_models,
        system_prompt=req.system_prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    return ChatResponse(
        request_id=result.request_id,
        response=result.final_response,
        mode=result.mode,
        models_used=[
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "latency_ms": m.latency_ms,
                "tokens": m.tokens_used,
                "cost_usd": m.cost_usd,
            }
            for m in result.models_used
        ],
        consensus_score=result.consensus_score,
        latency_ms=result.total_latency_ms,
        cost_usd=result.total_cost_usd,
        synthesized=result.synthesized,
        safety_passed=result.safety_passed,
        pii_detected=result.pii_detected,
    )


@router.post("/stream")
async def stream(
    req: ChatRequest,
    nexus: Annotated[NexusOrchestrator, Depends(get_nexus)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> StreamingResponse:
    if not tenant.get("nexus_enabled", True):
        raise HTTPException(status_code=403, detail="NEXUS not enabled for this tenant")

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user:
        raise HTTPException(status_code=422, detail="No user message found")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_generator():
        async for chunk in nexus.stream(
            prompt=last_user.content,
            mode=req.mode,
            tenant_id=tenant["id"],
            messages=messages,
            system_prompt=req.system_prompt,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/compare")
async def compare(
    req: ChatRequest,
    nexus: Annotated[NexusOrchestrator, Depends(get_nexus)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> dict:
    if not req.model_override or len(req.model_override) < 2:
        raise HTTPException(status_code=422, detail="model_override must have ≥2 models for comparison")

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user:
        raise HTTPException(status_code=422, detail="No user message found")

    result = await nexus.orchestrate(
        prompt=last_user.content,
        mode=NexusMode.MULTI_MODEL,
        tenant_id=tenant["id"],
        messages=[{"role": m.role, "content": m.content} for m in req.messages],
        override_models=req.model_override,
        max_models=len(req.model_override),
    )

    return {
        "request_id": result.request_id,
        "prompt": last_user.content,
        "models": [
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "response": m.response,
                "latency_ms": m.latency_ms,
                "tokens": m.tokens_used,
                "cost_usd": m.cost_usd,
                "confidence": m.confidence,
            }
            for m in result.models_used
        ],
        "consensus_score": result.consensus_score,
        "synthesized_response": result.final_response,
        "total_cost_usd": result.total_cost_usd,
    }


@router.get("/status")
async def nexus_status(nexus: Annotated[NexusOrchestrator, Depends(get_nexus)]) -> dict:
    from app.services.model_router import MODEL_REGISTRY

    return {
        "nexus": "online",
        "version": "3.0.0",
        "models_registered": len(MODEL_REGISTRY),
        "capabilities": ["chat", "code", "reasoning", "search_rag", "multi_model", "fast", "creative"],
        "consensus_threshold": 0.75,
        "max_parallel_models": 5,
    }
