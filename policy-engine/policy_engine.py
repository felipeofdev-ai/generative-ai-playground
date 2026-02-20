import yaml
from pathlib import Path

class PolicyEngine:
    def __init__(self, policy_file: str = "policy-engine/policies.yaml"):
        self.policies = yaml.safe_load(Path(policy_file).read_text())

    def is_model_allowed(self, tenant_plan: str, model: str) -> bool:
        allowed = self.policies["policies"]["allowed_models_per_tenant"].get(tenant_plan, [])
        return model in allowed
