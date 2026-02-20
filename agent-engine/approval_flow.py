def require_human_approval(risk_level: str) -> bool:
    return risk_level in {"high", "critical"}
