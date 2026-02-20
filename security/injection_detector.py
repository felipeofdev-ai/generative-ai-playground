SUSPICIOUS_PATTERNS = ["ignore previous instructions", "exfiltrate", "system prompt"]

def detect_prompt_injection(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in SUSPICIOUS_PATTERNS)
