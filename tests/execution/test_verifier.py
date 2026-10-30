import asyncio
from jev_gateway.execution.verifier import JevAnswerVerifier, VerificationRequest, EVENT
from jev_gateway.routing.jev_client import JevReply


class Client:
    async def decide(self, state, questions, *, deadline_seconds=None):
        assert 'reference' not in state
        assert state['generated_answer']=='4'
        assert questions['valid']['type']=='noul'
        return JevReply('jev-1.13.0', {'valid':{'type':'noul','noul':.91}},
                        {'input_tokens':10,'output_tokens':2}, 5.)


def test_answer_judgment_preserves_event_and_identity():
    request=VerificationRequest('r', ({'role':'user','content':'2+2?'},), '4','small','local')
    decision=asyncio.run(JevAnswerVerifier(Client()).judge(request))
    assert decision.probability==.91 and decision.event==EVENT
    assert decision.answer_sha256==request.answer_sha256
    assert decision.usage['output_tokens']==2
