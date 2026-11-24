import asyncio

from laya_gateway.config import from_env
from laya_gateway.routing.admission import request_for
from laya_gateway.routing.laya_choice import LayaChoiceRouter


class Runtime:
    async def decide(self, state, questions):
        assert questions["route"]["type"] == "choice"
        return type("Reply", (), {
            "model": "typed-decisions",
            "answers": {"route": {
                "type": "choice", "choice": "medium",
                "probabilities": {"small": .2, "medium": .8},
            }},
            "usage": {"input_tokens": 12},
            "duration_ms": 3.5,
        })()


def test_native_laya_choice_preserves_probability_meaning_and_identity():
    settings = from_env()
    request = request_for(settings, ({"role": "user", "content": "Calculate 4+4"},), 32, "p")
    result = asyncio.run(LayaChoiceRouter(settings, Runtime()).decide(request))
    assert result.tier == "medium"
    assert result.probability_event == "Laya routing choice among eligible tiers"
    assert result.question_version == "laya-routing-choice-v2"
    assert result.decision_model == "typed-decisions"
