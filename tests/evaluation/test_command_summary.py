from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from jev_gateway.evaluation import commands
from jev_gateway.evaluation.commands import _run_summary, _select_prompts
from jev_gateway.evaluation.records import Attempt, Result


def _result(*, reuse_of=None, response='answer', attempts=1, outcome='correct'):
    now=datetime.now(timezone.utc)
    return Result(
        run_id='run', prompt_id='prompt', task='math', split='validation',
        dataset_revision='dataset', source_revision='source', template_fingerprint='template',
        settings_fingerprint='settings', tier='small', backend='http://localhost', model='model',
        raw_response=response, parsed_answer='1', score=1 if outcome=='correct' else 0,
        outcome=outcome, started_at=now, ended_at=now, execution='real', reuse_of=reuse_of,
        attempts=tuple(Attempt(started_at=now, ended_at=now, outcome=outcome) for _ in range(attempts)),
    )


def test_summary_separates_checkpoint_rows_from_new_backend_work():
    reused=_result(reuse_of='original')
    fresh=_result(attempts=2, outcome='backend_error', response=None)

    assert _run_summary([reused, fresh]) == {
        'results':2,
        'checkpoint_reused':1,
        'new_backend_attempts':2,
        'new_responses':0,
        'outcomes':{'correct':1,'incorrect':0,'parse_error':0,'backend_error':1,'evaluator_error':0,'blocked':0},
    }


def test_task_filter_selects_in_manifest_order_before_applying_limit(monkeypatch):
    prompts=[SimpleNamespace(task=task, prompt_id=str(index)) for index,task in enumerate(('math','code','choice','math','choice'))]
    monkeypatch.setattr(commands,'load',lambda path,split: prompts)

    selected=_select_prompts('manifest','train',1,['choice','math'])

    assert [prompt.prompt_id for prompt in selected]==['0']


def test_task_filter_requires_a_positive_limit_and_a_matching_prompt(monkeypatch):
    monkeypatch.setattr(commands,'load',lambda path,split:[SimpleNamespace(task='math')])
    with pytest.raises(ValueError,match='max-prompts'):
        _select_prompts('manifest','train',0)
    with pytest.raises(ValueError,match='no prompts'):
        _select_prompts('manifest','train',10,['code'])
