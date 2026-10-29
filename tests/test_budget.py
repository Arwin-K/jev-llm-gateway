import asyncio
from dataclasses import replace
import pytest
from jev_gateway.budget import BudgetExceeded, FrontierBudget
from jev_gateway.config import from_env


def test_budget_admission(monkeypatch):
    for key, value in {
        "JEV_FRONTIER_MODEL": "paid-model", "JEV_FRONTIER_API_KEY": "secret",
        "JEV_FRONTIER_MAX_REQUESTS": "1", "JEV_FRONTIER_MAX_TOKENS": "1000",
        "JEV_FRONTIER_MAX_USD": "1", "JEV_FRONTIER_INPUT_USD_PER_MILLION": "1",
        "JEV_FRONTIER_OUTPUT_USD_PER_MILLION": "1",
    }.items():
        monkeypatch.setenv(key, value)
    budget = FrontierBudget(from_env())

    async def run():
        await budget.reserve([{"content": "hello"}], 5)
        with pytest.raises(BudgetExceeded):
            await budget.reserve([{"content": "hello"}], 5)

    asyncio.run(run())
    assert budget.requests == 1
