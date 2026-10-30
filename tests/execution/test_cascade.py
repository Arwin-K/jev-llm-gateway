import asyncio
import time
from jev_gateway.execution.acceptance import AcceptancePolicy
from jev_gateway.execution.cascade import CascadeEngine, ExecutionRequest
from jev_gateway.execution.verifier import VerificationDecision, EVENT, QUESTION_VERSION


class Generator:
    def __init__(self): self.calls=[]
    async def generate(self,tier,messages,max_output_tokens,temperature,deadline_seconds):
        self.calls.append(tier)
        return {'choices':[{'message':{'content':tier}}],'usage':{'completion_tokens':1}}


class Verifier:
    async def judge(self,request,*,deadline_seconds=None):
        return VerificationDecision(request.request_id,request.answer_sha256,
                                    .2 if request.tier=='small' else .9,EVENT,
                                    QUESTION_VERSION,'jev',1.,{})


def test_rejection_escalates_once_and_preserves_attempts():
    generator=Generator()
    engine=CascadeEngine(generator,Verifier(),AcceptancePolicy(.8,'validation-a'),
                         {'small':'s','medium':'m','frontier':'f'})
    request=ExecutionRequest('r',({'role':'user','content':'x'},),16,None,('small','medium'),time.monotonic()+5)
    result=asyncio.run(engine.run(request))
    assert result.status=='accepted_verified' and result.accepted_tier=='medium'
    assert [a.outcome for a in result.attempts]==['rejected','accepted_verified']
    assert generator.calls==['small','medium']
