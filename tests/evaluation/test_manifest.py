from pathlib import Path
import pytest
from laya_gateway.evaluation.manifest import build, load, save, validate


def test_grouped_split_and_test_gate(tmp_path, monkeypatch):
    from laya_gateway.evaluation import manifest
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


def test_template_revision_keeps_split_assignment(tmp_path, monkeypatch):
    import json
    from laya_gateway.evaluation import manifest
    from laya_gateway.evaluation.manifest import same_assignment
    monkeypatch.setattr(manifest, 'TARGETS', {'math':10,'choice':10,'code':10})
    (tmp_path/'gsm8k-train.jsonl').write_text(''.join(json.dumps({'source_index':i,'question':f'Number {i}?','answer':f'#### {i}'})+'\n' for i in range(20)))
    (tmp_path/'mmlu-test.jsonl').write_text(''.join(json.dumps({'source_index':i,'question':f'Question {i}?','choices':['a','b','c','d'],'answer':i%4,'subject':'s'})+'\n' for i in range(20)))
    (tmp_path/'mbpp-sanitized.jsonl').write_text(''.join(json.dumps({'task_id':i,'prompt':f'Write f{i}','test_list':[f'assert f{i}() == 1']})+'\n' for i in range(20)))
    v1, v2 = build(tmp_path, version='v1'), build(tmp_path, version='v2')
    same_assignment(v1, v2)
    assert {p.template_fingerprint for p in v1}.isdisjoint({p.template_fingerprint for p in v2})
    with pytest.raises(ValueError):
        same_assignment(v1, [p.model_copy(update={'split':'test' if p.split=='train' else p.split}) for p in v2])


def test_loading_validation_does_not_validate_test_prompt_rows(tmp_path):
    import json
    from pydantic import ValidationError

    base = {'prompt_id':'math:one', 'task':'math', 'dataset':'fixture',
            'dataset_revision':'r1', 'source_split':'train', 'source_id':'1',
            'source_revision':'r1', 'group_id':'math:g1',
            'template_fingerprint':'template-v1', 'prompt':'validation prompt'}
    validation = {**base, 'split':'validation'}
    locked_test = {**base, 'prompt':None, 'split':'test'}
    path = tmp_path / 'manifest.jsonl'
    path.write_text(json.dumps(validation)+'\n'+json.dumps(locked_test)+'\n')

    prompts = load(path, 'validation')
    assert [prompt.prompt for prompt in prompts] == ['validation prompt']
    with pytest.raises(PermissionError):
        load(path, 'test')
    with pytest.raises(ValidationError):
        load(path, 'test', allow_test=True)
