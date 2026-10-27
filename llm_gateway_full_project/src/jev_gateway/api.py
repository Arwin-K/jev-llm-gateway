"""OpenAI-style text-only HTTP surface with explicit tier selection."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .config import Settings, from_env


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


def create_app(settings: Settings | None = None):
    app = FastAPI(title="Jev gateway", version="0.1.0")
    app.state.settings = settings or from_env()

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
    async def chat(request: ChatRequest):
        if request.model == "frontier" and not app.state.settings.frontier_enabled:
            raise HTTPException(status_code=503, detail="frontier disabled: configure key, model, rates, and positive caps")
        raise HTTPException(status_code=503, detail="backend transport not yet connected")

    return app


app = create_app()
