import asyncio
from laya_gateway.execution.verifier import LayaAnswerVerifier, VerificationRequest, EVENT
from laya_gateway.routing.laya_runtime import DecisionReply


class Client:
    async def decide(self, state, questions, *, deadline_seconds=None):
        assert 'reference' not in state
        assert state['generated_answer']=='4'
        assert questions['valid']['type']=='noul'
        return DecisionReply('typed-decisions', {'valid':{'type':'noul','noul':.91}},
                        {'input_tokens':10,'output_tokens':2}, 5.)


def test_answer_judgment_preserves_event_and_identity():
    request=VerificationRequest('r', ({'role':'user','content':'2+2?'},), '4','small','local')
    decision=asyncio.run(LayaAnswerVerifier(Client()).judge(request))
    assert decision.probability==.91 and decision.event==EVENT
    assert decision.answer_sha256==request.answer_sha256
    assert decision.usage['output_tokens']==2
