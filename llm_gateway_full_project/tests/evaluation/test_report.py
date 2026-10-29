from types import SimpleNamespace
from jev_gateway.evaluation.report import quality_report


def test_failures_and_missing_remain_in_denominators():
    prompts=[SimpleNamespace(prompt_id=str(i),task='math') for i in range(4)]
    results=[SimpleNamespace(prompt_id='0',tier='small',outcome='correct',cost_status='unknown'),SimpleNamespace(prompt_id='1',tier='small',outcome='incorrect',cost_status='unknown'),SimpleNamespace(prompt_id='2',tier='small',outcome='backend_error',cost_status='unknown')]
    row=next(r for r in quality_report(prompts,results,('small',))['rows'] if r['task']=='math')
    assert row['expected']==4 and row['observed']==3 and row['missing']==1
    assert row['accuracy_scored']==.5 and row['correct_completion_rate']==.25 and row['completion_failure_rate']==.25
