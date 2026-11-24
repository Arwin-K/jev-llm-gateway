import asyncio
from dataclasses import replace
import pytest
from laya_gateway.config import from_env
from laya_gateway.evaluation.records import Prompt
from laya_gateway.routing.evaluate import collect, select_prompts


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
    from laya_gateway.routing import evaluate
    from laya_gateway.routing.contracts import RoutingError

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


def test_existing_output_path_is_rejected_before_router_calls(tmp_path, monkeypatch):
    from laya_gateway.routing import evaluate

    runs = tmp_path / 'runs'
    runs.mkdir()
    output = runs / 'existing.jsonl'
    output.write_text('preserve this file\n')
    manifest = tmp_path / 'manifest.jsonl'
    manifest.write_text('unused by patched loader\n')
    prompt = Prompt(prompt_id='p1',task='math',split='validation',dataset='x',
                    dataset_revision='d',source_split='train',source_id='1',
                    source_revision='s',group_id='g',template_fingerprint='t',prompt='2+2?')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(evaluate, 'load', lambda path, split: [prompt])
    calls = []

    async def collect(*args, **kwargs):
        calls.append(True)
        return []

    monkeypatch.setattr(evaluate, 'collect', collect)
    with pytest.raises(SystemExit):
        evaluate.main(['--policy','always-small','--max-prompts','1','--max-decisions','1',
                       '--manifest',str(manifest),'--output',str(output)])
    assert calls == []
    assert output.read_text() == 'preserve this file\n'
