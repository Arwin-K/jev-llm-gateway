import asyncio
from dataclasses import replace
import pytest
from jev_gateway.config import from_env
from jev_gateway.evaluation.records import Prompt
from jev_gateway.routing.evaluate import collect, select_prompts


def test_bounded_fixed_decisions_have_no_generation_cost_claim():
    prompts=[Prompt(prompt_id=str(i),task='math',split='validation',dataset='x',
                    dataset_revision='d',source_split='train',source_id=str(i),
                    source_revision='s',group_id=str(i),template_fingerprint='t',prompt='2+2?')
             for i in range(3)]
    settings=replace(from_env(),router_policy='always-small')
    records=asyncio.run(collect(prompts,settings,max_decisions=2))
    assert len(records)==2 and all(r['status']=='selected' for r in records)
    assert records[0]['selection']['decision_charge_usd']==0
    assert records[0]['selection']['execution']=='deterministic_local'


def test_decision_errors_preserve_safe_cause_category(monkeypatch):
    import json
    from jev_gateway.routing import evaluate
    from jev_gateway.routing.contracts import RoutingError

    class BrokenRouter:
        name = 'prompted-small'
        version = '1'
        async def decide(self, request):
            try:
                json.loads('{')
            except json.JSONDecodeError as cause:
                raise RoutingError('no valid selection') from cause

    monkeypatch.setattr(evaluate, 'build', lambda settings, transport: (BrokenRouter(), []))
    prompt = Prompt(prompt_id='broken',task='math',split='validation',dataset='x',
                    dataset_revision='d',source_split='train',source_id='1',
                    source_revision='s',group_id='g',template_fingerprint='t',prompt='2+2?')
    records=asyncio.run(collect([prompt],replace(from_env(),router_policy='prompted-small'),max_decisions=1))
    assert records == [{'status':'error','prompt_id':'broken','split':'validation','policy':'prompted-small','version':'1',
                        'error_category':'RoutingError','cause_category':'JSONDecodeError',
                        'router_raw_response':'{'}]


def test_exact_prompt_selection_is_bounded_and_validation_scoped():
    prompts=[Prompt(prompt_id=str(i),task='math',split='validation',dataset='x',
                    dataset_revision='d',source_split='train',source_id=str(i),
                    source_revision='s',group_id=str(i),template_fingerprint='t',prompt='2+2?')
             for i in range(3)]
    assert [p.prompt_id for p in select_prompts(prompts,2,['2','0'])] == ['0','2']
    with pytest.raises(ValueError):
        select_prompts(prompts,2,['0','0'])
    with pytest.raises(ValueError):
        select_prompts(prompts,2,['test-only'])
