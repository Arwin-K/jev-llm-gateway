from pathlib import Path
import pytest
from jev_gateway.evaluation.manifest import build, load, save, validate


def test_grouped_split_and_test_gate(tmp_path, monkeypatch):
    from jev_gateway.evaluation import manifest
    monkeypatch.setattr(manifest, 'TARGETS', {'math':10,'choice':10,'code':10})
    (tmp_path/'gsm8k-train.jsonl').write_text(''.join(__import__('json').dumps({'source_index':i,'question':f'Number {i}?','answer':f'#### {i}'})+'\n' for i in range(20)))
    (tmp_path/'mmlu-test.jsonl').write_text(''.join(__import__('json').dumps({'source_index':i,'question':f'Question {i}?','choices':['a','b','c','d'],'answer':i%4,'subject':'s'})+'\n' for i in range(20)))
    (tmp_path/'mbpp-sanitized.jsonl').write_text(''.join(__import__('json').dumps({'task_id':i,'prompt':f'Write f{i}','test_list':['assert True']})+'\n' for i in range(20)))
    prompts = build(tmp_path)
    assert len(prompts) == 30
    path = tmp_path/'manifest.jsonl'; save(prompts,path)
    assert len(load(path,'validation')) == 6
    with pytest.raises(PermissionError): load(path,'test')
    validate(prompts)
