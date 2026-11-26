"""Single-shot local chat orchestration for the CLI."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import uuid

from .config import Settings
from .routing.admission import request_for
from .routing.contracts import require_eligible
from .routing.laya_choice import LayaChoiceRouter
from .routing.laya_runtime import LayaRuntime
from .transport import BackendTransport


@dataclass(frozen=True)
class ChatResult:
    tier: str
    model: str
    answer: str
    decision_ms: float | None


async def complete_local(settings: Settings, prompt: str, *, tier: str = "auto",
                         max_tokens: int | None = None,
                         transport: BackendTransport | None = None,
                         runtime: LayaRuntime | None = None) -> ChatResult:
    """Route in-process with Laya, then generate using the configured local model backend."""
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if tier not in {"auto", "small", "medium"}:
        raise ValueError("CLI chat supports auto, small, or medium local tiers")
    limit = max_tokens or settings.max_output_tokens
    if not 1 <= limit <= settings.max_output_tokens:
        raise ValueError("max_tokens is outside the configured server policy")

    messages = ({"role": "user", "content": prompt},)
    decision_ms = None
    selected = tier
    owns_runtime = runtime is None
    runtime = runtime or LayaRuntime(settings)
    owns_transport = transport is None
    transport = transport or BackendTransport(settings.timeout_seconds)
    try:
        if tier == "auto":
            await runtime.initialize()
            request = request_for(settings, messages, limit, uuid.uuid4().hex)
            request = replace(request, eligible_tiers=tuple(
                candidate for candidate in request.eligible_tiers if candidate in {"small", "medium"}))
            decision = require_eligible(await runtime_decision(runtime, request), request)
            selected = decision.tier
            decision_ms = decision.duration_ms
        backend = settings.backend(selected)
        payload = {"model": backend.model,
                   "messages": list(messages),
                   "max_tokens": limit,
                   "stream": False}
        data = await transport.complete(backend, payload)
        answer = data["choices"][0]["message"]["content"]
        if not isinstance(answer, str):
            raise ValueError("local generator returned a non-text answer")
        return ChatResult(selected, backend.model, answer, decision_ms)
    finally:
        if owns_runtime:
            runtime.close()
        if owns_transport:
            await transport.close()


async def runtime_decision(runtime, request):
    router = LayaChoiceRouter(runtime.settings, runtime)
    return await router.decide(request)
