import json

from jev_gateway.day6.freeze import audit


def test_freeze_audit_counts_unique_scored_prompts_and_stays_closed(tmp_path):
    manifest = tmp_path / 'manifest.jsonl'
    manifest.write_text(''.join(json.dumps({'split': split, 'prompt_id': split})+'\n'
                                for split in ('train', 'validation', 'test')))
    results = tmp_path / 'results.jsonl'
    row = {'split': 'validation', 'prompt_id': 'validation', 'tier': 'small',
           'execution': 'real', 'score': 1, 'outcome': 'correct'}
    results.write_text((json.dumps(row)+'\n') * 2)
    config = tmp_path / 'config.json'
    config.write_text('{}')
    report = audit(manifest, [results], config)
    assert report['scored_observations']['validation/small'] == 1
    assert not report['ready_for_test']
    assert report['manifest_counts']['test'] == 1


def test_freeze_audit_flags_mixed_generation_identity(tmp_path):
    manifest = tmp_path / 'manifest.jsonl'
    manifest.write_text(json.dumps({'split': 'validation', 'prompt_id': 'one'})+'\n')
    results = tmp_path / 'results.jsonl'
    rows = [{'split': 'validation', 'prompt_id': 'one', 'tier': 'small', 'execution': 'real',
             'score': 1, 'outcome': 'correct', 'model': model, 'settings_fingerprint': 'same'}
            for model in ('old', 'new')]
    results.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    config = tmp_path / 'config.json'
    config.write_text('{}')
    assert 'small: mixed model, settings, or template identities' in audit(manifest, [results], config)['identity_issues']


def _task_scoped_fixture(tmp_path, rows, generation_settings=None):
    manifest = tmp_path / 'manifest.jsonl'
    manifest.write_text(''.join(json.dumps({'split': 'validation', 'prompt_id': row['prompt_id']})+'\n'
                                for row in rows))
    results = tmp_path / 'results.jsonl'
    results.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'generation_settings': generation_settings or {}}))
    return audit(manifest, [results], config)


def test_freeze_audit_allows_distinct_templates_across_tasks(tmp_path):
    rows = [
        {'split': 'validation', 'prompt_id': 'math1', 'task': 'math', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'model_revision': 'sha256:x', 'settings_fingerprint': 'settings', 'template_fingerprint': 'math-v2'},
        {'split': 'validation', 'prompt_id': 'choice1', 'task': 'choice', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'model_revision': 'sha256:x', 'settings_fingerprint': 'settings', 'template_fingerprint': 'choice-v2'},
    ]
    report = _task_scoped_fixture(tmp_path, rows)
    assert report['identity_issues'] == []


def test_freeze_audit_flags_template_change_within_task(tmp_path):
    rows = [
        {'split': 'validation', 'prompt_id': 'math1', 'task': 'math', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'settings_fingerprint': 'settings', 'template_fingerprint': 'math-v2'},
        {'split': 'validation', 'prompt_id': 'math2', 'task': 'math', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'settings_fingerprint': 'settings', 'template_fingerprint': 'math-v1'},
    ]
    report = _task_scoped_fixture(tmp_path, rows)
    assert 'small: mixed model, settings, or template identities' in report['identity_issues']


def test_freeze_audit_matches_task_scoped_template_configuration(tmp_path):
    rows = [
        {'split': 'validation', 'prompt_id': 'math1', 'task': 'math', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'model_revision': 'sha256:x', 'settings_fingerprint': 'settings', 'template_fingerprint': 'math-v2'},
        {'split': 'validation', 'prompt_id': 'choice1', 'task': 'choice', 'tier': 'small',
         'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
         'model_revision': 'sha256:x', 'settings_fingerprint': 'settings', 'template_fingerprint': 'choice-v2'},
    ]
    expected = {'small': {'fingerprint': 'settings',
                         'templates': {'math': 'math-v2', 'choice': 'choice-v2'}}}
    assert _task_scoped_fixture(tmp_path, rows, expected)['identity_issues'] == []
    expected['small']['templates']['choice'] = 'wrong'
    assert 'small: records disagree with freeze configuration' in \
        _task_scoped_fixture(tmp_path, rows, expected)['identity_issues']


def test_legacy_template_configuration_requires_single_task_template(tmp_path):
    row = {'split': 'validation', 'prompt_id': 'math1', 'task': 'math', 'tier': 'small',
           'execution': 'real', 'score': 1, 'outcome': 'correct', 'model': 'local',
           'settings_fingerprint': 'settings', 'template_fingerprint': 'math-v2'}
    config = {'small': {'fingerprint': 'settings', 'template': 'math-v2'}}
    assert _task_scoped_fixture(tmp_path, [row], config)['identity_issues'] == []
    other = {**row, 'prompt_id': 'choice1', 'task': 'choice', 'template_fingerprint': 'choice-v2'}
    issues = _task_scoped_fixture(tmp_path, [row, other], config)['identity_issues']
    assert 'small: task-scoped templates required in freeze configuration' in issues
