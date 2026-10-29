import asyncio
from jev_gateway.config import from_env
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.jev_choice import JevChoiceRouter
from jev_gateway.routing.jev_client import JevReply


class Client:
    async def decide(self, state, questions):
        assert set(questions['route']['criteria']) == {'small','medium'}
        return JevReply('jev-1.13.0', {'route':{'type':'choice','choice':'medium',
                         'probabilities':{'small':.2,'medium':.8}, 'confidence':.8}},
                        {'input_tokens':12,'output_tokens':4}, 3.5)


def test_choice_preserves_probability_meaning_and_identity():
    settings=from_env()
    request=request_for(settings, ({'role':'user','content':'Calculate 4+4'},), 32, 'p')
    result=asyncio.run(JevChoiceRouter(settings, Client()).decide(request))
    assert result.tier=='medium' and result.probability_event.startswith('Jev routing choice')
    assert result.question_version=='routing-choice-v1' and result.decision_model=='jev-1.13.0'
