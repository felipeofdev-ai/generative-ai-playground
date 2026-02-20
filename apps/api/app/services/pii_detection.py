"""
NexusAI — PII Detection & Redaction
Detects and redacts sensitive data before sending to AI providers.
Supports: Email, Phone, CPF, CNPJ, Credit Card, SSN, IP, API Keys.
"""

import re
from dataclasses import dataclass


@dataclass
class PIIResult:
    has_pii: bool
    has_critical_pii: bool
    entities: list[dict]
    redacted_text: str
    original_text: str


PII_PATTERNS = [
    ("CREDIT_CARD", r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b", True),
    ("API_KEY", r"\b(?:sk-[a-zA-Z0-9]{32,}|sk-ant-[a-zA-Z0-9\-]{50,}|AIza[0-9A-Za-z\-_]{35})\b", True),
    ("AWS_KEY", r"\b(?:AKIA|AIPA|ABIA|ACCA)[0-9A-Z]{16}\b", True),
    ("EMAIL_ADDRESS", r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b", False),
    ("PHONE_NUMBER", r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[\s\-]?\d{4}\b", False),
    ("CPF", r"\b\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{2}\b", False),
    ("CNPJ", r"\b\d{2}[\.\-]?\d{3}[\.\-]?\d{3}[\./]?\d{4}[\.\-]?\d{2}\b", False),
    ("SSN", r"\b\d{3}[\-]?\d{2}[\-]?\d{4}\b", False),
    ("IP_ADDRESS", r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", False),
    ("IBAN", r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]?){0,16}\b", False),
    ("PASSPORT", r"\b[A-Z]{1,2}[0-9]{6,9}\b", False),
]


class PIIDetector:
    def __init__(self):
        self._compiled = [
            (name, re.compile(pattern, re.IGNORECASE), critical)
            for name, pattern, critical in PII_PATTERNS
        ]

    async def analyze(self, text: str) -> PIIResult:
        entities: list[dict] = []
        redacted = text
        has_critical = False

        for name, pattern, critical in self._compiled:
            matches = list(pattern.finditer(redacted))
            for match in matches:
                entities.append(
                    {
                        "type": name,
                        "start": match.start(),
                        "end": match.end(),
                        "value_length": len(match.group()),
                        "critical": critical,
                    }
                )
                if critical:
                    has_critical = True

            redacted = pattern.sub(f"[{name}]", redacted)

        return PIIResult(
            has_pii=bool(entities),
            has_critical_pii=has_critical,
            entities=entities,
            redacted_text=redacted,
            original_text=text,
        )

    async def should_block(self, text: str) -> bool:
        result = await self.analyze(text)
        return result.has_critical_pii

    def get_stats(self, results: list[PIIResult]) -> dict:
        by_type: dict[str, int] = {}
        for r in results:
            for e in r.entities:
                by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        return {
            "total_requests": len(results),
            "pii_detected": sum(1 for r in results if r.has_pii),
            "critical_pii": sum(1 for r in results if r.has_critical_pii),
            "by_type": by_type,
        }
