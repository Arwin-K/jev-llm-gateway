"""Compare repeated unprofiled serving runs without dropping regressions."""

import argparse
import statistics
from pathlib import Path

from .common import digest, read_json, write_new


def compare(paths: list[Path]) -> dict:
    rows = [read_json(path) for path in paths]
    if len(rows) < 6 or {r.get('label') for r in rows} != {'baseline', 'candidate'}:
        raise ValueError('at least three baseline and three candidate runs required')
    if any(sum(r.get('label') == label for r in rows) < 3 for label in ('baseline', 'candidate')):
        raise ValueError('at least three runs per condition required')
    if any(r.get('schema') != 'jev.day6.benchmark.v1' or r.get('origin') != 'live_client'
           or r.get('success_count', 0) == 0 for r in rows):
        raise ValueError('all runs must contain actual successful live requests')
    constant_keys = ('workload_sha256', 'endpoint', 'arrival', 'interval_seconds',
                     'concurrency_cap', 'warmup_requests', 'timeout_seconds', 'request_count')
    for key in constant_keys:
        if len({str(row[key]) for row in rows}) != 1:
            raise ValueError(f'incompatible runs: {key}')
    if any(row.get('diagnostic_only') for row in rows):
        raise ValueError('profile runs cannot enter headline comparison')
    if any(rows[i]['label'] == rows[i-1]['label'] for i in range(1, len(rows))):
        raise ValueError('supply runs in alternating condition order')
    summaries = {}
    for label in ('baseline', 'candidate'):
        group = [row for row in rows if row['label'] == label]
        summaries[label] = {
            'run_ids': [r['run_id'] for r in group],
            'config_sha256': list({r['config_sha256'] for r in group}),
            'p50_ms_by_run': [r['latency_ms']['p50'] for r in group],
            'p95_ms_by_run': [r['latency_ms']['p95'] for r in group],
            'throughput_success_per_second_by_run': [r['throughput_success_per_second'] for r in group],
            'success_count_by_run': [r['success_count'] for r in group],
            'error_count_by_run': [r['error_count'] for r in group],
            'completion_tokens_by_run': [sum(x['completion_tokens'] for x in r['records']
                                              if x['phase'] == 'measured' and isinstance(x.get('completion_tokens'), int))
                                         for r in group],
            'gpu_snapshots_by_run': [[r.get('gpu_snapshot_before'), r.get('gpu_snapshot_after')]
                                     for r in group],
        }
        if len(summaries[label]['config_sha256']) != 1:
            raise ValueError(f'{label} config changed across repetitions')
        summaries[label]['median_p95_ms'] = statistics.median(summaries[label]['p95_ms_by_run'])
    if summaries['baseline']['config_sha256'] == summaries['candidate']['config_sha256']:
        raise ValueError('candidate configuration did not change')
    return {'schema': 'jev.day6.comparison.v1', 'input_sha256': [digest(p) for p in paths],
            'run_order': [{'label': r['label'], 'run_id': r['run_id']} for r in rows],
            'workload_sha256': rows[0]['workload_sha256'], 'summaries': summaries,
            'median_p95_difference_ms': summaries['candidate']['median_p95_ms']-summaries['baseline']['median_p95_ms'],
            'interpretation': 'client_observed_only'}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    write_new(args.output, compare(args.run))


if __name__ == '__main__':
    main()
