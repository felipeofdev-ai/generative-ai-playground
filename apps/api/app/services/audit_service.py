"""
NexusAI — Audit Service
Append-only, cryptographically hash-chained audit log.
Every entry references the hash of the previous entry — tamper-evident.
"""

import hashlib
import json
import uuid
from datetime import UTC, datetime

import structlog

log = structlog.get_logger(__name__)

_GENESIS_HASH = "0" * 64


class AuditService:
    def __init__(self):
        self._last_hash: str = _GENESIS_HASH

    def _compute_hash(self, entry: dict) -> str:
        canonical = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    async def log(
        self,
        tenant_id: str,
        event: str,
        resource: str,
        actor_id: str | None = None,
        resource_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> str:
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "event": event,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "prev_hash": self._last_hash,
            "created_at": datetime.now(UTC).isoformat(),
        }
        entry_hash = self._compute_hash(entry)
        entry["entry_hash"] = entry_hash
        self._last_hash = entry_hash

        log.info("audit.event", event=event, resource=resource, tenant_id=tenant_id, hash=entry_hash[:16])
        return entry_id

    async def log_inference(
        self,
        tenant_id: str,
        user_id: str,
        request_id: str,
        model: str,
        provider: str,
        latency_ms: float,
        cost_usd: float,
        safety_passed: bool,
        pii_detected: bool,
        prompt_hash: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        status_code: int = 200,
        error_message: str | None = None,
    ) -> str:
        return await self.log(
            tenant_id=tenant_id,
            actor_id=user_id,
            event="inference.completed",
            resource="inference",
            resource_id=request_id,
            details={
                "model": model,
                "provider": provider,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "safety_passed": safety_passed,
                "pii_detected": pii_detected,
                "prompt_hash": prompt_hash,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "status_code": status_code,
                "error_message": error_message,
            },
        )

    async def log_auth(self, tenant_id: str, user_id: str, event: str, ip: str | None = None) -> str:
        return await self.log(
            tenant_id=tenant_id,
            actor_id=user_id,
            event=event,
            resource="auth",
            ip_address=ip,
        )

    async def log_api_key(self, tenant_id: str, actor_id: str, event: str, key_id: str) -> str:
        return await self.log(
            tenant_id=tenant_id,
            actor_id=actor_id,
            event=event,
            resource="api_key",
            resource_id=key_id,
        )

    async def verify_chain(self, entries: list[dict]) -> tuple[bool, int | None]:
        prev_hash = _GENESIS_HASH
        for i, entry in enumerate(entries):
            stored_hash = entry.pop("entry_hash", "")
            computed = self._compute_hash(entry)
            entry["entry_hash"] = stored_hash
            if computed != stored_hash:
                return False, i
            if entry.get("prev_hash") != prev_hash:
                return False, i
            prev_hash = stored_hash
        return True, None
