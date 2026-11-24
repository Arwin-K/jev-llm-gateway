"""Descriptive paired-group bootstrap for saved small/medium validation outcomes."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from laya_gateway.day6.uncertainty import paired_difference


def _read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(index, small_path, medium_paths, *, repetitions=2000, seed=23):
    # The compact index contains IDs, groups, tasks and split labels; it has no prompt text.
    validation = {}
    for row in _read_rows(index):
        if row['split'] == 'validation':
            validation[row['prompt_id']] = row

    sources = {'small': [small_path], 'medium': medium_paths}
    results = {'small': {}, 'medium': {}}
    for tier, paths in sources.items():
        for path in paths:
            for row in _read_rows(path):
                if row.get('split') != 'validation' or row.get('tier') != tier:
                    continue
                if row['prompt_id'] not in validation:
                    raise ValueError(f'non-validation prompt in {path}')
                # The supplemental row is deliberately last and reclassifies mbpp:401.
                results[tier][row['prompt_id']] = row

    tasks = sorted({row['task'] for row in validation.values()})
    reports = {}
    all_left, all_right, all_groups = {}, {}, {}
    for task in tasks:
        left, right, groups = {}, {}, {}
        transitions = Counter()
        for prompt_id, index_row in validation.items():
            if index_row['task'] != task:
                continue
            small = results['small'].get(prompt_id)
            medium = results['medium'].get(prompt_id)
            if small is None or medium is None:
                continue
            if (small.get('template_fingerprint') != medium.get('template_fingerprint') or
                    small.get('settings_fingerprint') != medium.get('settings_fingerprint')):
                raise ValueError(f'incompatible paired identities for {prompt_id}')
            if small.get('outcome') not in ('correct', 'incorrect') or \
               medium.get('outcome') not in ('correct', 'incorrect'):
                continue
            left[prompt_id] = float(small['outcome'] == 'correct')
            right[prompt_id] = float(medium['outcome'] == 'correct')
            groups[prompt_id] = index_row['group_id']
            transitions[(small['outcome'], medium['outcome'])] += 1
        if left:
            reports[task] = paired_difference(left, right, groups=groups,
                                               repetitions=repetitions, seed=seed)
            reports[task]['transitions'] = {
                'both_correct': transitions[('correct', 'correct')],
                'small_correct_medium_incorrect': transitions[('correct', 'incorrect')],
                'small_incorrect_medium_correct': transitions[('incorrect', 'correct')],
                'both_incorrect': transitions[('incorrect', 'incorrect')],
            }
            all_left.update(left)
            all_right.update(right)
            all_groups.update(groups)
    if not all_left:
        raise ValueError('no complete paired binary validation outcomes')
    overall = paired_difference(all_left, all_right, groups=all_groups,
                                repetitions=repetitions, seed=seed)
    return {
        'run_id': 'medium-validation-paired-group-bootstrap-20261120',
        'split': 'validation',
        'comparison': 'medium accuracy minus small accuracy, paired on identical prompt IDs',
        'unit': 'prompt-group cluster',
        'method': overall['method'], 'seed': seed, 'repetitions': repetitions,
        'overall': overall, 'by_task': reports,
        'result_sources': {tier: [{'path': str(p), 'sha256': _sha256(p)} for p in paths]
                           for tier, paths in sources.items()},
        'index_source': {'path': str(index), 'sha256': _sha256(index),
                         'used_fields': ['prompt_id', 'task', 'split', 'group_id']},
        'limits': [
            'Binary-scored validation prompts only; parse errors and other nonbinary outcomes are excluded.',
            'The mbpp:401 saved answer uses the supplemental SyntaxError-based incorrect classification.',
            'This descriptive validation interval is not a selected routing threshold or a held-out generalization estimate.',
            'No test prompt text or reference was read; no model or paid-provider request was made.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=Path('docs/day2-manifest-index.jsonl'))
    parser.add_argument('--small', type=Path, default=Path('runs/day2-run-ddd52bb7b6c74b15b68a1df581e8ba1b.jsonl'))
    parser.add_argument('--medium', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repetitions', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=23)
    parser.add_argument('--mbpp401-overlay', type=Path,
                        default=Path('evidence/day8/medium-validation-code-mbpp401-rescore-20261120.jsonl'))
    args = parser.parse_args(argv)
    medium = args.medium or [
        Path('runs/day2-run-1024c23932c74897a9c95604c7f88836.jsonl'),
        Path('runs/day2-run-66afe463970d4f04900c50c204c1510f.jsonl'),
    ]
    medium.append(args.mbpp401_overlay)
    report = build(args.index, args.small, medium,
                   repetitions=args.repetitions, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(args.output), 'overall': report['overall'],
                      'by_task': report['by_task']}, indent=2))


if __name__ == '__main__':
    main()
