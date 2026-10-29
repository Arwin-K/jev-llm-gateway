import asyncio
import pytest
from jev_gateway.config import from_env
from jev_gateway.evaluation.datasets import gsm8k
from jev_gateway.evaluation.runner import RunLimits, RunBudget, evaluate_batch, evaluate_one


class FakeTransport:
    def __init__(self): self.calls=0
    async def complete(self,backend,payload):
        self.calls+=1
        return {'model':backend.model,'choices':[{'message':{'content':'Answer: 2'},'finish_reason':'stop'}], 'usage':{'prompt_tokens':10,'completion_tokens':3}}


def test_runner_caps_and_paid_gate():
    prompt=gsm8k({'question':'1+1?', 'answer':'#### 2'},0).model_copy(update={'split':'validation'})
    settings=from_env(); transport=FakeTransport()
    limits=RunLimits(max_requests=1,max_tokens=1000,max_usd=0,concurrency=2)
    results=asyncio.run(evaluate_batch([prompt],['small','medium'],'r',settings,transport,limits))
    assert transport.calls==1 and len(results)==2 and {r.outcome for r in results}=={'correct','blocked'}
    with pytest.raises(PermissionError):
        asyncio.run(evaluate_one(prompt,'frontier','r',settings,transport,RunBudget(limits),limits))
    with pytest.raises(ValueError):
        asyncio.run(evaluate_batch([prompt.model_copy(update={'split':'test'})],['small'],'r',settings,transport,limits))


def test_resumption_avoids_second_call(tmp_path):
    from jev_gateway.evaluation.checkpoint import Checkpoints
    prompt=gsm8k({'question':'1+1?', 'answer':'#### 2'},0).model_copy(update={'split':'validation'})
    transport=FakeTransport(); store=Checkpoints(tmp_path); limits=RunLimits(2,10000,0)
    first=asyncio.run(evaluate_batch([prompt],['small'],'first',from_env(),transport,limits,checkpoints=store))
    second=asyncio.run(evaluate_batch([prompt],['small'],'second',from_env(),transport,limits,checkpoints=store))
    assert transport.calls==1 and second[0].run_id=='first' and second[0].reuse_of=='first'


def test_reported_usage_overrun_stops_future_admission():
    settings=from_env(); limits=RunLimits(2,1000,0)
    budget=RunBudget(limits)
    async def check():
        assert await budget.reserve('x','small',settings)
        await budget.reconcile('small',settings,{'prompt_tokens':1001,'completion_tokens':1})
        assert not await budget.reserve('x','small',settings)
    asyncio.run(check())
