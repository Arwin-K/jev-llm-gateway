"""Gate a one-factor serving candidate on observed baseline evidence."""

import argparse
import copy
from pathlib import Path

from .common import digest, read_json, write_new


def prepare(config: Path, baseline: list[Path], *, new_token_budget: int,
            observation: str, explanation: str, expected: str, regression: str) -> dict:
    if len(baseline) < 3 or not all((observation, explanation, expected, regression)):
        raise ValueError('three baselines and a complete falsifiable hypothesis are required')
    settings = read_json(config)
    old = settings['max_num_batched_tokens']
    if new_token_budget <= 0 or new_token_budget == old:
        raise ValueError('candidate must change one positive batch-token budget')
    records = [read_json(path) for path in baseline]
    if any(row.get('schema') != 'jev.day6.benchmark.v1' or row.get('origin') != 'live_client'
           or row.get('success_count', 0) == 0 or row.get('config_sha256') != digest(config)
           for row in records):
        raise ValueError('real successful baseline records with matching config required')
    if len({row['workload_sha256'] for row in records}) != 1:
        raise ValueError('baseline workloads differ')
    changed = copy.deepcopy(settings)
    changed['max_num_batched_tokens'] = new_token_budget
    return {'schema': 'jev.day6.candidate.v1', 'baseline_run_ids': [r['run_id'] for r in records],
            'baseline_record_sha256': [digest(p) for p in baseline],
            'workload_sha256': records[0]['workload_sha256'],
            'factor': 'max_num_batched_tokens', 'before': old, 'after': new_token_budget,
            'observation': observation, 'explanation': explanation,
            'expected_benefit': expected, 'possible_regression': regression,
            'candidate_config': changed}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, action='append', required=True)
    parser.add_argument('--new-token-budget', type=int, required=True)
    parser.add_argument('--observation', required=True)
    parser.add_argument('--explanation', required=True)
    parser.add_argument('--expected', required=True)
    parser.add_argument('--regression', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    write_new(args.output, prepare(args.config, args.baseline,
                                   new_token_budget=args.new_token_budget,
                                   observation=args.observation, explanation=args.explanation,
                                   expected=args.expected, regression=args.regression))


if __name__ == '__main__':
    main()
