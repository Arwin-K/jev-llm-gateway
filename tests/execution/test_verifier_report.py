import hashlib
from datetime import datetime, timezone
from jev_gateway.evaluation.records import Result
from jev_gateway.execution.verifier_report import VerificationRecord, measure


def test_error_denominators_are_distinct():
    now=datetime.now(timezone.utc)
    results=[]; judgments=[]
    for prompt,answer,outcome,score,prob in [('a','wrong','incorrect',0,.9),('b','right','correct',1,.2)]:
        results.append(Result(run_id='r',prompt_id=prompt,task='math',split='validation',dataset_revision='d',
                              source_revision='s',template_fingerprint='t',settings_fingerprint='f',
                              tier='small',backend='local',model='m',raw_response=answer,score=score,
                              outcome=outcome,started_at=now,ended_at=now))
        judgments.append(VerificationRecord(prompt,'validation','small','m','f',
                         hashlib.sha256(answer.encode()).hexdigest(),prob,None,'q1','jev'))
    report=measure(judgments,results,threshold=.8,config_id='validation-a')
    assert report['wrong_accept_rate_among_wrong']==1
    assert report['correct_reject_rate_among_correct']==1
    assert report['wrong_fraction_among_accepted']==1
    assert report['verification_coverage']==1
