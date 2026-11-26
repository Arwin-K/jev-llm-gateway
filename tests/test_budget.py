import asyncio
import pytest
from laya_gateway.budget import BudgetExceeded, FrontierBudget
from laya_gateway.config import from_env


def test_budget_admission(monkeypatch):
    for key, value in {
        "LAYA_GATEWAY_FRONTIER_MODEL": "paid-model", "LAYA_GATEWAY_FRONTIER_API_KEY": "secret",
        "LAYA_GATEWAY_FRONTIER_MAX_REQUESTS": "1", "LAYA_GATEWAY_FRONTIER_MAX_TOKENS": "1000",
        "LAYA_GATEWAY_FRONTIER_MAX_USD": "1", "LAYA_GATEWAY_FRONTIER_INPUT_USD_PER_MILLION": "1",
        "LAYA_GATEWAY_FRONTIER_OUTPUT_USD_PER_MILLION": "1",
    }.items():
        monkeypatch.setenv(key, value)
    budget = FrontierBudget(from_env())

    async def run():
        await budget.reserve([{"content": "hello"}], 5)
        with pytest.raises(BudgetExceeded):
            await budget.reserve([{"content": "hello"}], 5)

    asyncio.run(run())
    assert budget.requests == 1
