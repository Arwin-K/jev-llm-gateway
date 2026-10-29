import asyncio
import pytest
from jev_gateway.config import from_env
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.contracts import RoutingError
from jev_gateway.routing.jev_client import JevReply
from jev_gateway.routing.jev_threshold import JevThresholdRouter


class Client:
    async def decide(self, state, questions):
        assert set(questions)=={'small','medium'}
        return JevReply('jev-1.13.0', {t:{'type':'noul','noul':p} for t,p in
                        [('small',.4),('medium',.9)]}, {'input_tokens':20,'output_tokens':5}, 2.0)


def test_success_questions_have_distinct_event_and_threshold():
    settings=from_env()
    request=request_for(settings, ({'role':'user','content':'x'},), 32, 'p')
    router=JevThresholdRouter(settings,Client(),{'small':.8,'medium':.8,'frontier':.8},selection_id='validation-v1')
    decision=asyncio.run(router.decide(request))
    assert decision.tier=='medium' and decision.probabilities['small']==.4
    assert 'externally scores correct' in decision.probability_event
    router=JevThresholdRouter(settings,Client(),{'small':.95,'medium':.95,'frontier':.95},selection_id='validation-v1')
    with pytest.raises(RoutingError):
        asyncio.run(router.decide(request))
