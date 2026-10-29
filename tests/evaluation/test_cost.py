from datetime import date
from types import SimpleNamespace
from jev_gateway.evaluation.cost import ApiRate, account_attempts, capacity_cost


def test_cost_all_attempts_and_idle_capacity():
    rate=ApiRate('m',2,4,date(2026,10,28),'https://example.com/rates')
    attempts=[SimpleNamespace(charge_usd=None,prompt_tokens=100,completion_tokens=50),SimpleNamespace(charge_usd=None,prompt_tokens=200,completion_tokens=100)]
    assert account_attempts(attempts,rate)['charge_usd']==0.0012000000000000001
    assert account_attempts(attempts)['status']=='unknown'
    assert account_attempts([SimpleNamespace(charge_usd=.02,prompt_tokens=None,completion_tokens=None)])['status']=='known_charge'
    assert capacity_cost(2,10,3)=={'status':'modeled_capacity','charge_usd':20,'idle_hours':7}


def test_rate_model_must_match():
    import pytest
    from jev_gateway.evaluation.cost import attach_cost
    with pytest.raises(ValueError):
        attach_cost(SimpleNamespace(model='a'),ApiRate('b',1,1,date(2026,10,28),'https://example.com'))
