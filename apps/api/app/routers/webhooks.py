"""Webhook management."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: list[str]
    secret: str | None = None


@router.get("/")
async def list_webhooks() -> dict:
    return {"webhooks": []}


@router.post("/", status_code=201)
async def create_webhook(req: WebhookCreate) -> dict:
    return {"id": "wh_abc123", "name": req.name, "url": req.url, "events": req.events}


@router.post("/{webhook_id}/test")
async def test_webhook(webhook_id: str) -> dict:
    _ = webhook_id
    return {"delivered": True, "status_code": 200, "latency_ms": 142}


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: str) -> None:
    _ = webhook_id
