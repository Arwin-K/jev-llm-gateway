import asyncio
from dataclasses import replace

import pytest

from laya_gateway.config import from_env
from laya_gateway.routing.contracts import RoutingError
from laya_gateway.routing.laya_runtime import LayaRuntime


class FakeLayaRouter:
    def __init__(self):
        self.calls = []

    def predict(self, state, questions, *, model):
        self.calls.append((state, questions, model))
        return {
            "routing": {"model": model},
            "answers": {"route": {
                "type": "choice", "choice": "small",
                "probabilities": {"small": 0.8, "medium": 0.2},
            }},
            "usage": {"input_tokens": 9, "output_tokens": 0, "windows": 1},
        }


def test_native_runtime_uses_laya_python_router_without_http():
    settings = from_env()
    fake = FakeLayaRouter()
    runtime = LayaRuntime(settings, router=fake)
    reply = asyncio.run(runtime.decide(
        {"messages": [{"role": "user", "content": "hello"}]},
        {"route": {"type": "choice", "instructions": "choose", "criteria": {"small": "s", "medium": "m"}}},
    ))
    assert reply.model == "typed-decisions"
    assert reply.answers["route"]["choice"] == "small"
    assert reply.usage == {"input_tokens": 9, "output_tokens": 0}
    assert fake.calls[0][2] == "typed-decisions"


def test_native_runtime_normalizes_noul_question_for_laya():
    questions = LayaRuntime._laya_questions({"valid": {"type": "noul", "instructions": "is valid?"}})
    assert questions["valid"]["criteria"] == {
        "true": "The following statement is true: is valid?",
        "false": "The following statement is false: is valid?",
    }
    assert questions["valid"]["labels"] == {"true": "A", "false": "B"}


def test_native_runtime_enforces_request_cap_before_model_call():
    settings = replace(from_env(), laya_max_requests=1)
    fake = FakeLayaRouter()
    runtime = LayaRuntime(settings, router=fake)
    kwargs = ({"messages": "hello"}, {"route": {"type": "choice", "criteria": {"small": "s", "medium": "m"}}})
    asyncio.run(runtime.decide(*kwargs))
    with pytest.raises(RoutingError, match="cap"):
        asyncio.run(runtime.decide(*kwargs))
    assert len(fake.calls) == 1
