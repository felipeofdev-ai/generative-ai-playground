import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AuditEntry:
    event: str
    payload: dict
    timestamp: str
    prev_hash: str
    hash: str


class ImmutableAuditTrail:
    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._last_hash = "genesis"

    def append(self, event: str, payload: dict) -> AuditEntry:
        timestamp = datetime.now(timezone.utc).isoformat()
        data = {"event": event, "payload": payload, "timestamp": timestamp, "prev_hash": self._last_hash}
        digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        entry = AuditEntry(event=event, payload=payload, timestamp=timestamp, prev_hash=self._last_hash, hash=digest)
        self._entries.append(entry)
        self._last_hash = digest
        return entry

    def verify_chain(self) -> bool:
        prev = "genesis"
        for e in self._entries:
            data = {"event": e.event, "payload": e.payload, "timestamp": e.timestamp, "prev_hash": e.prev_hash}
            expected = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            if e.prev_hash != prev or e.hash != expected:
                return False
            prev = e.hash
        return True
