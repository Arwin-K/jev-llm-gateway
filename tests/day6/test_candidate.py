import json

import pytest

from jev_gateway.day6.candidate import prepare
from jev_gateway.day6.common import digest


def test_candidate_rejects_empty_or_incompatible_baselines(tmp_path):
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'max_num_batched_tokens': 4096}))
    rows = []
    for i in range(3):
        path = tmp_path / f'{i}.json'
        path.write_text(json.dumps({'schema': 'jev.day6.benchmark.v1', 'origin': 'live_client',
                                    'success_count': 1, 'config_sha256': digest(config),
                                    'workload_sha256': 'same', 'run_id': str(i)}))
        rows.append(path)
    kwargs = dict(new_token_budget=2048, observation='queue', explanation='batch stalls',
                  expected='lower p95', regression='lower throughput')
    assert prepare(config, rows, **kwargs)['candidate_config']['max_num_batched_tokens'] == 2048
    with pytest.raises(ValueError, match='three baselines'):
        prepare(config, rows[:2], **kwargs)
    changed = json.loads(rows[1].read_text())
    changed['workload_sha256'] = 'different'
    rows[1].write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='workloads differ'):
        prepare(config, rows, **kwargs)
