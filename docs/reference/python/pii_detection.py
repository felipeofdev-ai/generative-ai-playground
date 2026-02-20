"""NexusAI — PII Detection Service (reference)."""
from dataclasses import dataclass
import structlog
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

log = structlog.get_logger(__name__)

@dataclass
class PIIResult:
    has_pii: bool
    has_critical_pii: bool
    entities: list[dict]
    redacted_text: str
    original_text: str
    risk_score: float = 0.0

class PIIDetector:
    CRITICAL_TYPES = {"CREDIT_CARD", "US_SSN", "BR_CPF", "BR_CNPJ", "PASSPORT"}
    DETECT_TYPES = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "US_SSN", "BR_CPF", "BR_CNPJ", "PASSPORT"]

    def __init__(self):
        try:
            registry = RecognizerRegistry(); registry.load_predefined_recognizers()
            self._analyzer = AnalyzerEngine(registry=registry)
            self._anonymizer = AnonymizerEngine()
            self._ready = True
        except Exception as exc:
            log.warning("pii.init.failed", error=str(exc))
            self._ready = False

    async def analyze(self, text: str, language: str = "en") -> PIIResult:
        if not self._ready or not text:
            return PIIResult(False, False, [], text, text)
        results = self._analyzer.analyze(text=text, language=language, entities=self.DETECT_TYPES, score_threshold=0.6)
        entities = [{"type": r.entity_type, "start": r.start, "end": r.end, "score": r.score} for r in results]
        has_critical = any(r.entity_type in self.CRITICAL_TYPES for r in results)
        operators = {t: OperatorConfig("replace", {"new_value": f"[{t}]"}) for t in self.DETECT_TYPES}
        redacted = self._anonymizer.anonymize(text=text, analyzer_results=results, operators=operators).text if results else text
        return PIIResult(bool(results), has_critical, entities, redacted, text, max((r.score for r in results), default=0.0))
