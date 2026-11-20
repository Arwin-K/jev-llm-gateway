from datetime import datetime, timezone

from jev_gateway.evaluation.commands import _run_summary
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
