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
