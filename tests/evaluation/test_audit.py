from types import SimpleNamespace
from jev_gateway.evaluation.audit import export


def test_audit_private_dev_only(tmp_path):
    prompts=[SimpleNamespace(prompt_id='a',split='validation',task='math',prompt='1+1',reference='2'),SimpleNamespace(prompt_id='b',split='test',task='math',prompt='secret',reference='9')]
    results=[SimpleNamespace(prompt_id='a',tier='small',raw_response='2',parsed_answer='2',outcome='correct',score=1,error_category=None),SimpleNamespace(prompt_id='b',tier='small',raw_response='9',parsed_answer='9',outcome='correct',score=1,error_category=None)]
    path=tmp_path/'audit.csv'; assert export(prompts,results,path)=={'math':1}
    assert 'secret' not in path.read_text() and 'pending_human_review' in path.read_text()
