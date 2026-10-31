import asyncio
import time
from jev_gateway.execution.acceptance import AcceptancePolicy
from jev_gateway.execution.cascade import CascadeEngine, ExecutionRequest
from jev_gateway.execution.modes import ModeExecutor
from jev_gateway.routing.contracts import Decision, RoutingRequest
from test_cascade import Generator, Verifier


class Router:
    async def decide(self,request):
        return Decision('medium','fixed','1',.1,request_id=request.request_id)


def test_modes_keep_route_and_verification_distinct():
    generator=Generator()
    engine=CascadeEngine(generator,Verifier(),AcceptancePolicy(.8,'validation-a'),
                         {'small':'s','medium':'m','frontier':'f'})
    executor=ModeExecutor(Router(),engine)
    request=ExecutionRequest('r',({'role':'user','content':'x'},),16,None,('small','medium'),time.monotonic()+5)
    routing=RoutingRequest(request.messages,16,'r','settings',('small','medium'))
    routed=asyncio.run(executor.run('route_first',request,routing))
    hybrid=asyncio.run(executor.run('hybrid',request,routing))
    cascade=asyncio.run(executor.run('cascade',request))
    assert routed.execution.status=='unverified_route_first' and routed.decision.tier=='medium'
    assert hybrid.execution.status=='accepted_verified' and hybrid.execution.accepted_tier=='medium'
    assert cascade.execution.attempts[0].tier=='small' and cascade.decision is None


def test_failed_primary_uses_compatible_trained_fallback_only():
    class Unavailable:
        async def decide(self, request):
            raise ValueError('Jev unavailable')
    generator=Generator()
    engine=CascadeEngine(generator,Verifier(),AcceptancePolicy(.8,'validation-a'),
                         {'small':'s','medium':'m','frontier':'f'})
    request=ExecutionRequest('r',({'role':'user','content':'x'},),16,None,('small','medium'),time.monotonic()+5)
    routing=RoutingRequest(request.messages,16,'r','settings',('small','medium'))
    routed=asyncio.run(ModeExecutor(Unavailable(),engine,Router()).run('route_first',request,routing))
    assert routed.decision.outcome == 'fallback_selected'
    assert routed.decision.fallback_reason == 'ValueError'
    assert routed.execution.accepted_tier == 'medium'
    unavailable=asyncio.run(ModeExecutor(Unavailable(),engine).run('route_first',request,routing))
    assert unavailable.execution.status == 'routing_failed'
