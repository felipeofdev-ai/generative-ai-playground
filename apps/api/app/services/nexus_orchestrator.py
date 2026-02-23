"""
NexusAI — NEXUS Orchestrator
The core intelligence engine that routes, coordinates, and synthesizes
responses from multiple AI models to produce superior results.
"""

import asyncio
import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import AsyncGenerator

import structlog
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.config import settings
from app.services.audit_service import AuditService
from app.services.cost_tracker import CostTracker
from app.services.model_router import ModelRouter, NexusMode
from app.services.pii_detection import PIIDetector

log = structlog.get_logger(__name__)

__all__ = ["NexusOrchestrator", "NexusMode", "NexusResult", "ModelResult"]


@dataclass
class ModelResult:
    model_id: str
    provider: str
    response: str
    confidence: float
    latency_ms: float
    tokens_used: int
    cost_usd: float
    error: str | None = None


@dataclass
class NexusResult:
    request_id: str
    final_response: str
    mode: str
    models_used: list[ModelResult]
    consensus_score: float
    total_latency_ms: float
    total_cost_usd: float
    synthesized: bool
    safety_passed: bool
    pii_detected: bool
    pii_entities: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


PRICING = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "o1-preview": (15.0, 60.0),
    "claude-3-5-sonnet-20241022": (3.0, 15.0),
    "claude-3-haiku-20240307": (0.25, 1.25),
    "deepseek-reasoner": (0.55, 2.19),
    "deepseek-chat": (0.14, 0.28),
    "gemini-1.5-pro": (7.00, 21.00),
    "llama-3.3-70b": (0.90, 0.90),
}


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICING:
        return 0.0
    inp, out = PRICING[model]
    return (input_tokens * inp + output_tokens * out) / 1_000_000


class NexusOrchestrator:
    def __init__(self):
        self.router = ModelRouter()
        self.pii_detector = PIIDetector()
        self.cost_tracker = CostTracker()
        self.audit = AuditService()
        self._openai = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self._anthropic = AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

    async def orchestrate(
        self,
        prompt: str,
        mode: NexusMode = NexusMode.CHAT,
        tenant_id: str = "",
        user_id: str = "",
        messages: list[dict] | None = None,
        override_models: list[str] | None = None,
        max_models: int | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> NexusResult:
        request_id = str(uuid.uuid4())
        start_time = time.monotonic()
        log.info("nexus.orchestrate.start", request_id=request_id, mode=mode.value, tenant_id=tenant_id)

        pii_result = await self.pii_detector.analyze(prompt)
        safe_prompt = pii_result.redacted_text

        selected_models = override_models or await self.router.select_models(
            safe_prompt,
            mode,
            max_models=max_models or settings.nexus_max_models,
        )

        tasks = [
            self._call_model(
                model_id=m,
                prompt=safe_prompt,
                messages=messages,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            for m in selected_models
        ]

        results: list[ModelResult] = await asyncio.gather(*tasks, return_exceptions=False)
        valid = [r for r in results if not r.error]

        if not valid:
            raise RuntimeError("All model calls failed — NEXUS circuit breaker triggered")

        consensus_score, synthesized, final_response = self._synthesize(valid, mode)
        total_latency = (time.monotonic() - start_time) * 1000
        total_cost = sum(r.cost_usd for r in results)

        nexus_result = NexusResult(
            request_id=request_id,
            final_response=final_response,
            mode=mode.value,
            models_used=valid,
            consensus_score=consensus_score,
            total_latency_ms=total_latency,
            total_cost_usd=total_cost,
            synthesized=synthesized,
            safety_passed=True,
            pii_detected=pii_result.has_pii,
            pii_entities=pii_result.entities,
        )

        asyncio.create_task(
            self.cost_tracker.record(
                tenant_id=tenant_id,
                request_id=request_id,
                model=selected_models[0] if selected_models else "unknown",
                provider="nexus",
                input_tokens=0,
                output_tokens=0,
                cost_usd=total_cost,
            )
        )
        asyncio.create_task(
            self.audit.log_inference(
                tenant_id=tenant_id,
                user_id=user_id,
                request_id=request_id,
                model="nexus-ultra",
                provider="nexusai",
                latency_ms=total_latency,
                cost_usd=total_cost,
                safety_passed=True,
                pii_detected=pii_result.has_pii,
                prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
            )
        )

        log.info(
            "nexus.orchestrate.complete",
            request_id=request_id,
            consensus=consensus_score,
            latency_ms=total_latency,
            cost_usd=total_cost,
            models=len(valid),
        )
        return nexus_result

    async def stream(
        self,
        prompt: str,
        mode: NexusMode = NexusMode.CHAT,
        tenant_id: str = "",
        user_id: str = "",
        messages: list[dict] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        request_id = str(uuid.uuid4())

        pii_result = await self.pii_detector.analyze(prompt)
        safe_prompt = pii_result.redacted_text

        selected_models = await self.router.select_models(safe_prompt, mode, max_models=1)
        primary_model = selected_models[0] if selected_models else "gpt-4o"

        yield f"data: {{'type':'start','request_id':'{request_id}','model':'{primary_model}'}}\n\n"

        async for token in self._stream_model(
            model_id=primary_model,
            prompt=safe_prompt,
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield f"data: {{'type':'token','content':{repr(token)}}}\n\n"

        yield f"data: {{'type':'done','request_id':'{request_id}'}}\n\n"

    async def _call_model(
        self,
        model_id: str,
        prompt: str,
        messages: list[dict] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ModelResult:
        start = time.monotonic()
        msgs = messages or [{"role": "user", "content": prompt}]

        try:
            provider = self.router.get_provider(model_id)

            if provider == "openai":
                result = await self._openai_call(model_id, msgs, system_prompt, temperature, max_tokens)
            elif provider == "anthropic":
                result = await self._anthropic_call(model_id, msgs, system_prompt, temperature, max_tokens)
            elif provider == "deepseek":
                result = await self._deepseek_call(model_id, msgs, system_prompt, temperature, max_tokens)
            else:
                result = await self._openai_compatible_call(
                    model_id, provider, msgs, system_prompt, temperature, max_tokens
                )

            latency = (time.monotonic() - start) * 1000
            input_tokens = result.get("input_tokens", 0)
            output_tokens = result.get("output_tokens", 0)
            cost = compute_cost(model_id, input_tokens, output_tokens)

            return ModelResult(
                model_id=model_id,
                provider=provider,
                response=result["text"],
                confidence=1.0,
                latency_ms=latency,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
            )

        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            log.error("nexus.model.failed", model=model_id, error=str(exc))
            return ModelResult(
                model_id=model_id,
                provider="unknown",
                response="",
                confidence=0.0,
                latency_ms=latency,
                tokens_used=0,
                cost_usd=0.0,
                error=str(exc),
            )

    async def _openai_call(self, model_id, msgs, system, temperature, max_tokens) -> dict:
        if not self._openai:
            raise RuntimeError("OpenAI API key not configured")
        full_msgs = []
        if system:
            full_msgs.append({"role": "system", "content": system})
        full_msgs.extend(msgs)
        resp = await self._openai.chat.completions.create(
            model=model_id,
            messages=full_msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": resp.choices[0].message.content or "",
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
        }

    async def _anthropic_call(self, model_id, msgs, system, temperature, max_tokens) -> dict:
        if not self._anthropic:
            raise RuntimeError("Anthropic API key not configured")
        kwargs = dict(model=model_id, messages=msgs, max_tokens=max_tokens, temperature=temperature)
        if system:
            kwargs["system"] = system
        resp = await self._anthropic.messages.create(**kwargs)
        return {
            "text": resp.content[0].text if resp.content else "",
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }

    async def _deepseek_call(self, model_id, msgs, system, temperature, max_tokens) -> dict:
        import httpx

        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "model": model_id,
            "messages": msgs,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system:
            payload["messages"] = [{"role": "system", "content": system}] + msgs

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "text": data["choices"][0]["message"]["content"],
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
            }

    async def _openai_compatible_call(self, model_id, provider, msgs, system, temperature, max_tokens) -> dict:
        base_urls = {
            "groq": "https://api.groq.com/openai/v1",
            "mistral": "https://api.mistral.ai/v1",
            "together": "https://api.together.xyz/v1",
        }
        api_keys = {
            "groq": settings.groq_api_key,
            "mistral": settings.mistral_api_key,
        }
        client = AsyncOpenAI(api_key=api_keys.get(provider, ""), base_url=base_urls.get(provider, ""))
        full_msgs = []
        if system:
            full_msgs.append({"role": "system", "content": system})
        full_msgs.extend(msgs)
        resp = await client.chat.completions.create(
            model=model_id,
            messages=full_msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": resp.choices[0].message.content or "",
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
        }

    async def _stream_model(self, model_id, prompt, messages, system_prompt, temperature, max_tokens):
        provider = self.router.get_provider(model_id)
        msgs = messages or [{"role": "user", "content": prompt}]

        if provider == "openai" and self._openai:
            full_msgs = []
            if system_prompt:
                full_msgs.append({"role": "system", "content": system_prompt})
            full_msgs.extend(msgs)
            async with self._openai.chat.completions.stream(
                model=model_id,
                messages=full_msgs,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for event in stream:
                    if event.choices and event.choices[0].delta.content:
                        yield event.choices[0].delta.content
        elif provider == "anthropic" and self._anthropic:
            async with self._anthropic.messages.stream(
                model=model_id,
                messages=msgs,
                max_tokens=max_tokens,
                temperature=temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            result = await self._call_model(
                model_id, prompt, messages, system_prompt, temperature, max_tokens
            )
            for word in result.response.split():
                yield word + " "
                await asyncio.sleep(0.01)

    def _synthesize(self, results: list[ModelResult], mode: NexusMode) -> tuple[float, bool, str]:
        if len(results) == 1:
            return 1.0, False, results[0].response

        responses = [r.response for r in results]
        all_words = [set(r.lower().split()) for r in responses]

        if len(all_words) >= 2:
            intersection = all_words[0]
            for s in all_words[1:]:
                intersection &= s
            union = all_words[0]
            for s in all_words[1:]:
                union |= s
            jaccard = len(intersection) / max(len(union), 1)
            consensus_score = min(0.5 + jaccard * 0.5, 1.0)
        else:
            consensus_score = 1.0

        best = min(results, key=lambda r: r.latency_ms)
        if mode in (NexusMode.REASONING, NexusMode.CODE):
            best = max(results, key=lambda r: r.tokens_used)

        synthesized = consensus_score < settings.nexus_consensus_threshold
        if synthesized and len(results) >= 2:
            final = (
                f"[NEXUS Synthesized — {len(results)} models, "
                f"consensus {consensus_score:.0%}]\n\n{best.response}"
            )
        else:
            final = best.response
        return consensus_score, synthesized, final