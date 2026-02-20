"""NexusAI — ADK Agent Runtime Adapter (reference).

Reference adapter showing how to attach an ADK-style agent runtime
into NexusAI orchestration boundaries.
"""
from dataclasses import dataclass
from typing import Protocol, Any

@dataclass
class AgentRunResult:
    output: str
    tokens_used: int
    cost_usd: float
    trace_id: str

class AgentRuntime(Protocol):
    async def run(self, *, agent_id: str, instruction: str, context: list[dict[str, Any]]) -> AgentRunResult: ...

class AdkRuntimeAdapter:
    """Adapter boundary to keep NexusAI decoupled from concrete ADK SDK versions."""

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime

    async def execute_agent(self, agent_id: str, prompt: str, context: list[dict[str, Any]] | None = None) -> AgentRunResult:
        ctx = context or []
        return await self.runtime.run(agent_id=agent_id, instruction=prompt, context=ctx)
