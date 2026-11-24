import asyncio

from laya_gateway.chat import complete_local
from laya_gateway.config import from_env
from laya_gateway.routing.laya_runtime import DecisionReply


class FakeRuntime:
    def __init__(self, settings):
        self.settings = settings
        self.initialized = False
        self.closed = False

    async def initialize(self):
        self.initialized = True

    async def decide(self, state, questions):
        assert questions["route"]["type"] == "choice"
        return DecisionReply("typed-decisions", {
            "route": {"type": "choice", "choice": "small",
                      "probabilities": {"small": .8, "medium": .2}},
        }, {}, 12.)

    def close(self):
        self.closed = True


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.closed = False

    async def complete(self, backend, payload):
        self.calls.append((backend, payload))
        return {"choices": [{"message": {"content": "local answer"}}]}

    async def close(self):
        self.closed = True


def test_auto_chat_decides_in_process_then_uses_local_backend():
    settings = from_env()
    runtime, transport = FakeRuntime(settings), FakeTransport()
    result = asyncio.run(complete_local(settings, "hello", runtime=runtime, transport=transport))
    assert runtime.initialized
    assert result.tier == "small" and result.model == settings.small.model
    assert result.answer == "local answer" and result.decision_ms == 12.
    backend, payload = transport.calls[0]
    assert backend.base_url == "http://127.0.0.1:11434/v1"
    assert payload["stream"] is False
    assert not runtime.closed and not transport.closed


def test_explicit_local_tier_skips_laya_decision():
    settings = from_env()
    runtime, transport = FakeRuntime(settings), FakeTransport()
    result = asyncio.run(complete_local(settings, "hello", tier="medium",
                                        runtime=runtime, transport=transport))
    assert not runtime.initialized
    assert result.tier == "medium" and result.decision_ms is None
    assert transport.calls[0][0] == settings.medium
