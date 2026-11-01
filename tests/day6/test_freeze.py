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
