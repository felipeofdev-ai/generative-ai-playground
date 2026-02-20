"""NexusAI — Audit Service (reference)."""
import hashlib, json
from datetime import datetime, UTC
import structlog

log = structlog.get_logger(__name__)
_last_hash = "genesis"

class AuditService:
    async def log_inference(self, request_id: str, tenant_id: str, user_id: str, prompt_hash: str, models_used: list[str], safety_passed: bool) -> None:
        await self._append({
            "event": "inference", "request_id": request_id, "tenant_id": tenant_id, "user_id": user_id,
            "prompt_hash": prompt_hash, "models_used": models_used, "safety_passed": safety_passed,
            "timestamp": datetime.now(UTC).isoformat(), "prev_hash": _last_hash,
        })

    async def _append(self, entry: dict) -> None:
        global _last_hash
        digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        _last_hash = digest
        log.info("audit.appended", event=entry["event"], hash=digest[:16])
