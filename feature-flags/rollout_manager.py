import random
import yaml
from pathlib import Path


class RolloutManager:
    def __init__(self, cfg_path: str = "feature-flags/model_rollout.yaml"):
        self.cfg = yaml.safe_load(Path(cfg_path).read_text())

    def choose_model(self) -> str:
        rollouts = self.cfg.get("rollouts", [])
        if not rollouts:
            return "default"
        r = random.randint(1, 100)
        c = 0
        for item in rollouts:
            c += int(item["traffic"])
            if r <= c:
                return item["model"]
        return rollouts[-1]["model"]
