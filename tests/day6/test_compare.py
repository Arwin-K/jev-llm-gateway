import json

import pytest

from jev_gateway.day6.compare import compare


def test_comparison_rejects_mismatched_workload(tmp_path):
    paths = []
    for i in range(6):
        label = 'baseline' if i % 2 == 0 else 'candidate'
        row = {'schema': 'jev.day6.benchmark.v1', 'origin': 'live_client',
               'label': label, 'run_id': str(i), 'success_count': 2, 'error_count': 0,
               'workload_sha256': 'same', 'config_sha256': label, 'endpoint': 'local',
               'arrival': 'burst', 'interval_seconds': 0, 'concurrency_cap': 2,
               'warmup_requests': 1, 'timeout_seconds': 20, 'request_count': 2,
               'latency_ms': {'p50': 10, 'p95': 12+i}, 'throughput_success_per_second': 1,
               'records': [{'phase': 'measured', 'completion_tokens': 8}]}
        path = tmp_path / f'{i}.json'
        path.write_text(json.dumps(row))
        paths.append(path)
    result = compare(paths)
    assert result['median_p95_difference_ms'] == 1
    changed = json.loads(paths[2].read_text())
    changed['workload_sha256'] = 'other'
    paths[2].write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='workload_sha256'):
        compare(paths)
