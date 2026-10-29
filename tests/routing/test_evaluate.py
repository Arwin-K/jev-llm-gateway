import asyncio
from dataclasses import replace
from jev_gateway.config import from_env
from jev_gateway.evaluation.records import Prompt
from jev_gateway.routing.evaluate import collect


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
