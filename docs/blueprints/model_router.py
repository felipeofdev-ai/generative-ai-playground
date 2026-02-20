class ModelRouter:
    async def select_models(self, prompt: str, max_models: int = 3) -> list[str]:
        # Reference blueprint only.
        models = ["gpt-4o", "claude-3-5-sonnet-20241022", "deepseek-reasoner"]
        return models[:max_models]
