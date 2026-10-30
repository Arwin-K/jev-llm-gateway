import hashlib
from datetime import datetime, timezone
from jev_gateway.evaluation.records import Prompt, Result
from jev_gateway.execution.comparison import ExecutionObservation, StageCost, compare


def test_real_replay_requires_matching_answer_identity():
    prompt=Prompt(prompt_id='p',task='math',split='validation',dataset='x',dataset_revision='d',
                  source_split='train',source_id='p',source_revision='s',group_id='g',
                  template_fingerprint='t',prompt='2+2?')
    now=datetime.now(timezone.utc)
    result=Result(run_id='r',prompt_id='p',task='math',split='validation',dataset_revision='d',
                  source_revision='s',template_fingerprint='t',settings_fingerprint='f',tier='small',
                  backend='local',model='m',raw_response='4',score=1,outcome='correct',
                  started_at=now,ended_at=now)
    observation=ExecutionObservation('p','validation','cascade','accepted_verified','small','m',
        hashlib.sha256(b'4').hexdigest(),'f',(StageCost('generation','small',None,'unknown'),),
        'real',20.)
    report=compare([prompt],[observation],[result])
    cascade=next(x for x in report if x['mode']=='cascade')
    assert cascade['independently_scored']==1 and cascade['total_charge_usd'] is None
    assert cascade['end_to_end_p50_ms']==20
    bad=ExecutionObservation(**(observation.__dict__ | {'answer_sha256':'wrong'}))
    assert next(x for x in compare([prompt],[bad],[result]) if x['mode']=='cascade')['unmatched_answer_identity']==1
