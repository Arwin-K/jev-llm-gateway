import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

audit_path = Path(__file__).resolve().parents[2] / 'scripts' / 'day8_prompted_router_v4_audit.py'
audit_spec = spec_from_file_location('prompted_router_v4_audit', audit_path)
audit_module = module_from_spec(audit_spec)
audit_spec.loader.exec_module(audit_module)
summarize = audit_module.summarize


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows))


def selected(prompt_id, tier='small', version='4'):
    return {
        'status': 'selected', 'prompt_id': prompt_id, 'version': version,
        'selection': {'tier': tier, 'decision_duration_ms': 12.5},
        'usage': {'prompt_tokens': 25, 'completion_tokens': 4, 'total_tokens': 29}
    }


def test_summarize_checks_split_and_version(tmp_path):
    decisions = tmp_path / 'decisions.jsonl'
    write_jsonl(decisions, [selected('train-1')])
    index = {'train-1': {'split': 'train', 'task': 'math'}}

    report = summarize(decisions, 'train', index)

    assert report['attempted'] == report['selected'] == 1
    assert report['selected_tiers'] == {'small': 1}
    assert report['decisions_by_task'] == {'math/selected': 1}
    assert report['usage_on_selected_decisions_only']['total_tokens'] == 29
    with pytest.raises(ValueError, match='do not match validation split'):
        summarize(decisions, 'validation', index)

    write_jsonl(decisions, [selected('train-1', version='3')])
    with pytest.raises(ValueError, match='non-v4'):
        summarize(decisions, 'train', index)


def test_summarize_rejects_duplicate_ids_and_joins_saved_outcomes(tmp_path):
    decisions = tmp_path / 'decisions.jsonl'
    outcomes = tmp_path / 'outcomes.jsonl'
    index = {
        'validation-1': {'split': 'validation', 'task': 'choice'},
        'validation-2': {'split': 'validation', 'task': 'code'}
    }
    write_jsonl(decisions, [selected('validation-1'), selected('validation-2', tier='medium')])
    write_jsonl(outcomes, [
        {'prompt_id': 'validation-1', 'split': 'validation', 'tier': 'small', 'outcome': 'correct'}
    ])

    report = summarize(decisions, 'validation', index, outcomes)

    assert report['saved_small_generator_outcomes_for_selected_prompts'] == {
        'correct': 1, 'missing_saved_result': 1
    }
    assert report['decisions_by_task'] == {'choice/selected': 1, 'code/selected': 1}
    write_jsonl(decisions, [selected('validation-1'), selected('validation-1')])
    with pytest.raises(ValueError, match='duplicate prompt ID'):
        summarize(decisions, 'validation', index)
