"""OpenAI-style text-only HTTP surface with explicit and automatic tier selection."""

from typing import Literal
import asyncio
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
from pydantic import BaseModel, ConfigDict, Field

from .config import Settings, from_env
from .budget import BudgetExceeded, FrontierBudget
from .transport import BackendTransport
from .tracing import RequestTrace
from .routing.admission import request_for
from .routing.contracts import RoutingError, require_eligible
from .routing.artifact import ArtifactError
from .routing.factory import build, fallback


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "developer", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: Literal["small", "medium", "frontier", "auto"]
    messages: list[Message] = Field(min_length=1)
    stream: bool = False
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    temperature: float | None = Field(default=None, ge=0, le=2)


def create_app(settings: Settings | None = None, transport: BackendTransport | None = None,
               router=None, fallback_router=None):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            for closer in app.state.router_closers:
                await closer.close()
            if transport is None:
                await app.state.transport.close()

    app = FastAPI(title="Jev gateway", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings or from_env()
    app.state.transport = transport or BackendTransport(app.state.settings.timeout_seconds)
    app.state.budget = FrontierBudget(app.state.settings)
    app.state.router = router
    app.state.fallback_router = fallback_router
    app.state.router_closers = []
    if router is None:
        try:
            app.state.router, app.state.router_closers = build(app.state.settings, app.state.transport)
        except (ValueError, OSError, ArtifactError, RoutingError) as exc:
            app.state.router_error = type(exc).__name__
    if fallback_router is None:
        app.state.fallback_router = fallback(app.state.settings)

    @app.get("/healthz")
    async def health():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readiness():
        # Process readiness; backend availability is reported per tier by doctor.
        return {"status": "ready", "backend_availability": "unchecked"}

    @app.get("/v1/models")
    async def models():
        s = app.state.settings
        return {"object": "list", "data": [
            {"id": tier, "object": "model", "backend_model": s.backend(tier).model,
             "enabled": tier != "frontier" or s.frontier_enabled}
            for tier in ("small", "medium", "frontier")
        ]}

    @app.post("/v1/chat/completions")
    async def chat(request: ChatRequest, response: Response):
        settings = app.state.settings
        max_tokens = request.max_tokens or settings.max_output_tokens
        if max_tokens > settings.max_output_tokens:
            raise HTTPException(status_code=422, detail="max_tokens exceeds server policy")
        trace = RequestTrace(request.model, 'pending')
        tier = request.model
        deadline = time.monotonic() + settings.timeout_seconds
        if tier == 'auto':
            if app.state.router is None:
                trace.finish('router_unavailable')
                raise HTTPException(status_code=503, detail='automatic router unavailable')
            routing_request = request_for(settings, tuple(m.model_dump() for m in request.messages),
                                          max_tokens, trace.request_id)
            try:
                decision = require_eligible(await asyncio.wait_for(
                    app.state.router.decide(routing_request), timeout=max(.001,deadline-time.monotonic())),
                    routing_request)
                trace.routing = {'policy':decision.policy, 'version':decision.version,
                                 'duration_ms':decision.duration_ms, 'outcome':decision.outcome,
                                 'fallback_reason':decision.fallback_reason,
                                 'probability_event':decision.probability_event,
                                 'question_version':decision.question_version,
                                 'decision_model':decision.decision_model,
                                 'usage':dict(decision.usage)}
            except (RoutingError, asyncio.TimeoutError, ValueError) as exc:
                if app.state.fallback_router is None:
                    trace.routing = {'policy':settings.router_policy,'outcome':'failed',
                                     'fallback_reason':type(exc).__name__}
                    trace.finish('router_error')
                    raise HTTPException(status_code=503, detail='automatic routing unavailable') from exc
                try:
                    decision = require_eligible(await asyncio.wait_for(
                        app.state.fallback_router.decide(routing_request),
                        timeout=max(.001,deadline-time.monotonic())), routing_request)
                    trace.routing = {'policy':decision.policy,'version':decision.version,
                                     'duration_ms':decision.duration_ms,'outcome':'fallback_selected',
                                     'fallback_reason':type(exc).__name__,
                                     'probability_event':decision.probability_event,
                                     'decision_model':decision.decision_model,
                                     'usage':dict(decision.usage)}
                except (RoutingError, asyncio.TimeoutError, ValueError) as fallback_exc:
                    trace.finish('router_error')
                    raise HTTPException(status_code=503, detail='automatic routing and fallback unavailable') from fallback_exc
            tier = decision.tier
        if tier == "frontier" and not settings.frontier_enabled:
            trace.finish('frontier_disabled')
            raise HTTPException(status_code=503, detail="frontier disabled: configure key, model, rates, and positive caps")
        backend = settings.backend(tier)
        trace.tier = tier
        trace.backend_model = backend.model
        if time.monotonic() >= deadline:
            trace.finish('deadline_exceeded')
            raise HTTPException(status_code=504, detail='request deadline exceeded before generation')
        payload = {"model": backend.model, "messages": [message.model_dump() for message in request.messages],
                   "max_tokens": max_tokens, "stream": request.stream}
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if tier == "frontier":
            try:
                await app.state.budget.reserve(payload["messages"], max_tokens)
            except BudgetExceeded as exc:
                raise HTTPException(status_code=429, detail=str(exc)) from exc
        try:
            if request.stream:
                upstream = await asyncio.wait_for(app.state.transport.open_stream(backend, payload),
                                                  timeout=max(.001, deadline-time.monotonic()))

                async def chunks():
                    try:
                        async with asyncio.timeout(max(.001, deadline-time.monotonic())):
                            async for part in upstream.aiter_raw():
                                yield part
                        trace.finish("ok", cost_status="reserved" if tier == "frontier" else "unpriced")
                    except BaseException:
                        trace.finish("stream_interrupted")
                        raise
                    finally:
                        await upstream.aclose()

                headers = {"x-jev-tier": tier, "x-jev-backend-model": backend.model,
                           "cache-control": "no-cache", "x-request-id": trace.request_id}
                if request.model == 'auto' and trace.routing:
                    headers['x-jev-policy'] = trace.routing['policy']
                    headers['x-jev-routing-outcome'] = trace.routing['outcome']
                return StreamingResponse(chunks(), media_type="text/event-stream", headers=headers)
            result = await asyncio.wait_for(app.state.transport.complete(backend, payload),
                                            timeout=max(.001, deadline-time.monotonic()))
        except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
            trace.finish("timeout")
            raise HTTPException(status_code=504, detail="backend deadline exceeded") from exc
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
            trace.finish("backend_error")
            raise HTTPException(status_code=502, detail="backend request failed") from exc
        trace.finish("ok", result.get("usage"), "reserved" if tier == "frontier" else "unpriced")
        response.headers["x-request-id"] = trace.request_id
        response.headers["x-jev-tier"] = tier
        response.headers["x-jev-backend-model"] = backend.model
        if request.model == 'auto' and trace.routing:
            response.headers['x-jev-policy'] = trace.routing['policy']
            response.headers['x-jev-routing-outcome'] = trace.routing['outcome']
        return result

    return app


app = create_app()
