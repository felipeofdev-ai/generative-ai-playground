JAILBREAK_CUES = ["jailbreak", "bypass safety", "developer mode"]

def is_jailbreak_attempt(text: str) -> bool:
    t = text.lower()
    return any(c in t for c in JAILBREAK_CUES)
