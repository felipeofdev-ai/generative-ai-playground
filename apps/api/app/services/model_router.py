"""
NexusAI — Model Router
Intelligent routing based on task type, cost, latency, and availability.
"""

import re
from enum import Enum

import structlog

from app.config import settings

log = structlog.get_logger(__name__)


class NexusMode(str, Enum):
    CHAT = "chat"
    CODE = "code"
    REASONING = "reasoning"
    SEARCH_RAG = "search_rag"
    MULTI_MODEL = "multi_model"
    FAST = "fast"
    CREATIVE = "creative"


class TaskType(str, Enum):
    GENERAL = "general"
    CODE = "code"
    MATH = "math"
    REASONING = "reasoning"
    CREATIVE = "creative"
    SEARCH = "search"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"


MODEL_REGISTRY = {
    "gpt-4o": {"provider": "openai", "strength": ["general", "code", "reasoning"], "latency": "medium", "cost_tier": "premium"},
    "gpt-4o-mini": {"provider": "openai", "strength": ["general", "fast"], "latency": "fast", "cost_tier": "cheap"},
    "o1-preview": {"provider": "openai", "strength": ["reasoning", "math"], "latency": "slow", "cost_tier": "expensive"},
    "claude-3-5-sonnet-20241022": {"provider": "anthropic", "strength": ["general", "code", "creative", "reasoning"], "latency": "medium", "cost_tier": "premium"},
    "claude-3-haiku-20240307": {"provider": "anthropic", "strength": ["fast", "summarization"], "latency": "fast", "cost_tier": "cheap"},
    "deepseek-reasoner": {"provider": "deepseek", "strength": ["reasoning", "math", "code"], "latency": "medium", "cost_tier": "cheap"},
    "deepseek-chat": {"provider": "deepseek", "strength": ["general", "code"], "latency": "fast", "cost_tier": "cheap"},
    "gemini-1.5-pro": {"provider": "google", "strength": ["general", "search", "creative"], "latency": "slow", "cost_tier": "expensive"},
    "llama-3.3-70b": {"provider": "groq", "strength": ["general", "fast"], "latency": "fast", "cost_tier": "cheap"},
    "mistral-large-latest": {"provider": "mistral", "strength": ["general", "code"], "latency": "medium", "cost_tier": "medium"},
}

MODE_MODELS: dict[NexusMode, list[str]] = {
    NexusMode.CHAT: ["claude-3-5-sonnet-20241022", "gpt-4o", "deepseek-chat"],
    NexusMode.CODE: ["claude-3-5-sonnet-20241022", "deepseek-reasoner", "gpt-4o"],
    NexusMode.REASONING: ["deepseek-reasoner", "o1-preview", "claude-3-5-sonnet-20241022"],
    NexusMode.SEARCH_RAG: ["gpt-4o", "claude-3-5-sonnet-20241022"],
    NexusMode.MULTI_MODEL: ["gpt-4o", "claude-3-5-sonnet-20241022", "deepseek-reasoner"],
    NexusMode.FAST: ["gpt-4o-mini", "claude-3-haiku-20240307", "llama-3.3-70b"],
    NexusMode.CREATIVE: ["claude-3-5-sonnet-20241022", "gpt-4o", "gemini-1.5-pro"],
}

TASK_MODELS: dict[TaskType, list[str]] = {
    TaskType.MATH: ["deepseek-reasoner", "o1-preview", "gpt-4o"],
    TaskType.CODE: ["claude-3-5-sonnet-20241022", "deepseek-reasoner", "gpt-4o"],
    TaskType.REASONING: ["deepseek-reasoner", "o1-preview", "claude-3-5-sonnet-20241022"],
    TaskType.CREATIVE: ["claude-3-5-sonnet-20241022", "gpt-4o", "gemini-1.5-pro"],
    TaskType.TRANSLATION: ["gpt-4o", "claude-3-5-sonnet-20241022"],
    TaskType.SUMMARIZATION: ["claude-3-haiku-20240307", "gpt-4o-mini"],
    TaskType.GENERAL: ["gpt-4o", "claude-3-5-sonnet-20241022"],
}

TASK_KEYWORDS = {
    TaskType.MATH: r"\b(calcul|integral|deriv|equation|matrix|solve|polynomial|theorem|proof|algebra|geometry|statistic|probabili)\b",
    TaskType.CODE: r"\b(code|function|class|debug|refactor|implement|script|python|javascript|typescript|rust|golang|sql|api|algorithm)\b",
    TaskType.REASONING: r"\b(reason|analyze|think|logic|deduce|infer|argument|evaluate|critique|compare|contrast|explain why)\b",
    TaskType.CREATIVE: r"\b(write|story|poem|creative|fiction|narrative|character|plot|metaphor|imagine|invent)\b",
    TaskType.TRANSLATION: r"\b(translat|convert to|in (spanish|french|portuguese|german|japanese|chinese|arabic|italian))\b",
    TaskType.SUMMARIZATION: r"\b(summar|tldr|brief|overview|key points|main points|condense|abstract)\b",
}


class ModelRouter:
    def _detect_task(self, prompt: str) -> TaskType:
        lower = prompt.lower()
        for task_type, pattern in TASK_KEYWORDS.items():
            if re.search(pattern, lower, re.IGNORECASE):
                return task_type
        return TaskType.GENERAL

    def get_provider(self, model_id: str) -> str:
        return MODEL_REGISTRY.get(model_id, {}).get("provider", "openai")

    async def select_models(
        self,
        prompt: str,
        mode: NexusMode,
        max_models: int = 3,
        exclude_providers: list[str] | None = None,
    ) -> list[str]:
        task = self._detect_task(prompt)
        if task in (TaskType.MATH, TaskType.CODE, TaskType.REASONING) and mode != NexusMode.FAST:
            candidates = TASK_MODELS.get(task, [])
        else:
            candidates = MODE_MODELS.get(mode, MODE_MODELS[NexusMode.CHAT])

        if exclude_providers:
            candidates = [m for m in candidates if MODEL_REGISTRY.get(m, {}).get("provider") not in exclude_providers]

        available = [m for m in candidates if self._is_available(m)]
        if not available:
            available = ["gpt-4o"] if self._is_available("gpt-4o") else list(MODEL_REGISTRY.keys())[:1]

        selected = available[:max_models]
        log.info("router.selected", task=task.value, mode=mode.value, models=selected)
        return selected

    def _is_available(self, model_id: str) -> bool:
        provider = MODEL_REGISTRY.get(model_id, {}).get("provider", "")
        key_map = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "deepseek": settings.deepseek_api_key,
            "google": settings.google_api_key,
            "groq": settings.groq_api_key,
            "mistral": settings.mistral_api_key,
        }
        key = key_map.get(provider, "")
        return bool(key) or settings.is_development
