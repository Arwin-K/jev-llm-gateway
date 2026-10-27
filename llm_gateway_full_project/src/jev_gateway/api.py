"""OpenAI-style text-only HTTP surface with explicit tier selection."""

from typing import Literal

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from .config import Settings, from_env
from .budget import BudgetExceeded, FrontierBudget
from .transport import BackendTransport


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "developer", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: Literal["small", "medium", "frontier"]
    messages: list[Message] = Field(min_length=1)
    stream: bool = False
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    temperature: float | None = Field(default=None, ge=0, le=2)


def create_app(settings: Settings | None = None, transport: BackendTransport | None = None):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            if transport is None:
                await app.state.transport.close()

    app = FastAPI(title="Jev gateway", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings or from_env()
    app.state.transport = transport or BackendTransport(app.state.settings.timeout_seconds)
    app.state.budget = FrontierBudget(app.state.settings)

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
        if request.model == "frontier" and not app.state.settings.frontier_enabled:
            raise HTTPException(status_code=503, detail="frontier disabled: configure key, model, rates, and positive caps")
        settings = app.state.settings
        backend = settings.backend(request.model)
        max_tokens = request.max_tokens or settings.max_output_tokens
        if max_tokens > settings.max_output_tokens:
            raise HTTPException(status_code=422, detail="max_tokens exceeds server policy")
        payload = {"model": backend.model, "messages": [message.model_dump() for message in request.messages],
                   "max_tokens": max_tokens, "stream": False}
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.model == "frontier":
            try:
                await app.state.budget.reserve(payload["messages"], max_tokens)
            except BudgetExceeded as exc:
                raise HTTPException(status_code=429, detail=str(exc)) from exc
        result = await app.state.transport.complete(backend, payload)
        response.headers["x-jev-tier"] = request.model
        response.headers["x-jev-backend-model"] = backend.model
        return result

    return app


app = create_app()
