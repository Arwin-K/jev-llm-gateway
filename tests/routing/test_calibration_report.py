from datetime import datetime, timezone
import pytest
from jev_gateway.evaluation.records import Result
from jev_gateway.routing.calibration_report import report, SUCCESS_EVENT


def test_success_calibration_uses_scored_result_not_router_opinion():
    now=datetime.now(timezone.utc)
    result=Result(run_id='r',prompt_id='p',task='math',split='validation',dataset_revision='d',
                  source_revision='s',template_fingerprint='t',settings_fingerprint='f',
                  tier='small',backend='local',model='m',raw_response='4',score=1,
                  outcome='correct',started_at=now,ended_at=now)
    decision={'status':'selected','selection':{'prompt_id':'p','tier':'small'},
              'probability_event':SUCCESS_EVENT,'probabilities':{'small':.8,'medium':.5}}
    measured=report('generator-success',[decision],[result],bins=2)
    assert measured['count']==1 and measured['expected']==2 and measured['missing']==1
    assert measured['brier']==pytest.approx(.04)
    assert report('oracle-tier',[decision],[result],[],bins=2)['status']=='insufficient_data'
