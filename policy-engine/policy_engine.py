from dataclasses import dataclass
from pathlib import Path


def _load_simple_yaml(text: str) -> dict:
    # Minimal parser for this repository's static policies format.
    policies = {
        "allowed_models_per_tenant": {},
        "max_tokens_per_call": 4096,
        "disallowed_topics": [],
        "required_pii_scan": True,
    }
    current_plan = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line == "policies:" or line == "allowed_models_per_tenant:":
            continue
        if line.startswith(("enterprise:", "starter:", "professional:")):
            plan, values = line.split(":", 1)
            models = values.strip().strip("[]")
            policies["allowed_models_per_tenant"][plan] = [m.strip() for m in models.split(",") if m.strip()]
            current_plan = plan
        elif line.startswith("max_tokens_per_call:"):
            policies["max_tokens_per_call"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("disallowed_topics:"):
            topics = line.split(":", 1)[1].strip().strip("[]")
            policies["disallowed_topics"] = [t.strip() for t in topics.split(",") if t.strip()]
        elif line.startswith("required_pii_scan:"):
            policies["required_pii_scan"] = line.split(":", 1)[1].strip().lower() == "true"
        elif current_plan and line.startswith("-"):
            policies["allowed_models_per_tenant"].setdefault(current_plan, []).append(line[1:].strip())
    return {"policies": policies}


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self, policy_file: str = "policy-engine/policies.yaml"):
        raw = Path(policy_file).read_text()
        try:
            import yaml  # optional dependency

            self.policies = yaml.safe_load(raw)
        except Exception:
            self.policies = _load_simple_yaml(raw)

    def is_model_allowed(self, tenant_plan: str, model: str) -> bool:
        allowed = self.policies["policies"]["allowed_models_per_tenant"].get(tenant_plan, [])
        return model in allowed

    def validate_tokens(self, tokens: int) -> PolicyDecision:
        max_tokens = int(self.policies["policies"].get("max_tokens_per_call", 4096))
        if tokens > max_tokens:
            return PolicyDecision(False, f"token_limit_exceeded:{tokens}>{max_tokens}")
        return PolicyDecision(True, "ok")

    def validate_topic(self, text: str) -> PolicyDecision:
        text_l = text.lower()
        blocked = self.policies["policies"].get("disallowed_topics", [])
        for topic in blocked:
            if topic.replace("-", " ") in text_l or topic in text_l:
                return PolicyDecision(False, f"blocked_topic:{topic}")
        return PolicyDecision(True, "ok")

    def enforce_request(self, *, tenant_plan: str, model: str, prompt: str, tokens: int) -> PolicyDecision:
        if not self.is_model_allowed(tenant_plan, model):
            return PolicyDecision(False, "model_not_allowed")
        tok = self.validate_tokens(tokens)
        if not tok.allowed:
            return tok
        top = self.validate_topic(prompt)
        if not top.allowed:
            return top
        return PolicyDecision(True, "ok")
