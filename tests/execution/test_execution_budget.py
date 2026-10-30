import asyncio
import time
import pytest
from jev_gateway.budget import FrontierBudget
from jev_gateway.config import from_env
from jev_gateway.execution.budget import ExecutionBudget, ExecutionLimit


def test_cumulative_requests_and_tokens_do_not_reset():
    settings=from_env()
    budget=ExecutionBudget(settings,deadline_at=time.monotonic()+5,max_requests=1,
                           max_tokens=10000,max_usd=0,frontier_budget=FrontierBudget(settings))
    async def scenario():
        await budget.reserve('generation',tier='small',content={'messages':[{'role':'user','content':'x'}]},output_tokens=8)
        with pytest.raises(ExecutionLimit):
            await budget.reserve('generation',tier='medium',content={'messages':[{'role':'user','content':'x'}]},output_tokens=8)
    asyncio.run(scenario())
    assert budget.requests==1 and len(budget.stages)==1


def test_frontier_cannot_be_admitted_when_disabled():
    settings=from_env()
    budget=ExecutionBudget(settings,deadline_at=time.monotonic()+5,max_requests=3,
                           max_tokens=10000,max_usd=1,frontier_budget=FrontierBudget(settings))
    with pytest.raises(ExecutionLimit):
        asyncio.run(budget.reserve('generation',tier='frontier',
                                   content={'messages':[{'role':'user','content':'x'}]},output_tokens=8))
