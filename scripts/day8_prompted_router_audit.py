"""Summarize saved prompted-router decisions without exposing prompt text."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def _read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)] if ordered else None


def _pilot(path, index, prompt_version):
    rows = _read(path)
    selected = Counter()
    errors = Counter()
    versions = Counter()
    for row in rows:
        prompt_id = row.get('prompt_id') or row.get('selection', {}).get('prompt_id')
        if prompt_id not in index or index[prompt_id]['split'] != 'train':
            raise ValueError(f'pilot row is not in train split: {prompt_id}')
        task = index[prompt_id]['task']
        if row['status'] == 'selected':
            selected[f"{task}/{row['selection']['tier']}"] += 1
            versions[row.get('version')] += 1
        else:
            errors[f"{task}/{row.get('error_category')}/{row.get('cause_category')}"] += 1
    if versions and versions != Counter({prompt_version: sum(versions.values())}):
        raise ValueError(f'pilot selection version mismatch in {path}')
    return {'attempted': len(rows), 'prompt_version': prompt_version,
            'selected': dict(selected), 'errors': dict(errors),
            'selected_row_versions': dict(versions), 'source_sha256': _sha(path)}


def build(index_path, validation_decisions, small_results, validation_diagnostics,
          train_v1, train_v2):
    index = {r['prompt_id']: r for r in _read(index_path)}
    decisions = _read(validation_decisions)
    prompt_ids = [r.get('prompt_id') or r.get('selection', {}).get('prompt_id') for r in decisions]
    if len(prompt_ids) != 500 or len(set(prompt_ids)) != 500:
        raise ValueError('expected 500 unique validation decisions')
    if any(pid not in index or index[pid]['split'] != 'validation' for pid in prompt_ids):
        raise ValueError('a routing decision is outside the validation split')
    errors, selected, by_task = Counter(), Counter(), Counter()
    latencies, usage = [], Counter()
    for row in decisions:
        task = index[row.get('prompt_id') or row['selection']['prompt_id']]['task']
        if row['status'] == 'selected':
            selection = row['selection']
            selected[selection['tier']] += 1
            by_task[(task, 'selected')] += 1
            latencies.append(selection['decision_duration_ms'])
            usage.update(row.get('usage', {}))
        else:
            errors[row.get('error_category')] += 1
            by_task[(task, 'error')] += 1

    outcomes = _read(small_results)
    small = {r['prompt_id']: r for r in outcomes if r['split'] == 'validation' and r['tier'] == 'small'}
    selected_outcomes = Counter()
    for row in decisions:
        if row['status'] != 'selected':
            continue
        selection = row['selection']
        result = small.get(selection['prompt_id']) if selection['tier'] == 'small' else None
        selected_outcomes[result['outcome'] if result else 'missing_saved_result'] += 1

    diagnostics = _read(validation_diagnostics)
    diagnostic_errors = Counter(
        f"{index[row['prompt_id']]['task']}/{row.get('error_category')}/{row.get('cause_category')}"
        for row in diagnostics if row['status'] == 'error')
    return {
        'run_id': 'prompted-small-audit-20261120',
        'validation': {
            'expected_prompts': 500, 'attempted_decisions': len(decisions),
            'selected': sum(selected.values()), 'selected_tiers': dict(selected),
            'errors': dict(errors),
            'errors_by_task': {f'{task}/{status}': n for (task, status), n in by_task.items()},
            'saved_small_generator_outcomes_for_selected_prompts': dict(selected_outcomes),
            'decision_duration_ms': {
                'n': len(latencies), 'median': _percentile(latencies, .5),
                'p95': _percentile(latencies, .95)},
            'usage_on_selected_decisions_only': dict(usage),
            'initial_run_version': sorted({str(r.get('version')) for r in decisions if r.get('version')}),
            'selected_response_count_note': 'These are matched saved small-tier outcomes, not generations made by the router run.'
        },
        'targeted_validation_error_diagnostics': {
            'attempted': len(diagnostics), 'errors': dict(diagnostic_errors),
            'scope': 'two exact failed prompt IDs; diagnostic cause categories only, response bodies not retained'
        },
        'training_prompt_development_pilots': {
            'version_1': _pilot(train_v1, index, '1'),
            'version_2': _pilot(train_v2, index, '2')
        },
        'input_sha256': {str(p): _sha(p) for p in
                         (index_path, validation_decisions, small_results,
                          validation_diagnostics, train_v1, train_v2)},
        'limits': [
            'The initial 500-prompt validation run records only generic RoutingError for failures; it cannot be retroactively assigned parser cause categories.',
            'Two targeted validation failures and 30 disjoint train-pilot decisions reported JSONDecodeError; this does not establish a cause for every initial failure.',
            'Saved generator outcomes are joined only to successful route selections for descriptive analysis; router run made no generation requests.',
            'Prompt version 2 was explored on train prompts only and was not evaluated on validation.',
            'No Laya, frontier, paid-provider, or held-out test call/result is included.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=Path('docs/day2-manifest-index.jsonl'))
    parser.add_argument('--validation-decisions', type=Path, required=True)
    parser.add_argument('--small-results', type=Path, required=True)
    parser.add_argument('--validation-diagnostics', type=Path, required=True)
    parser.add_argument('--train-v1', type=Path, required=True)
    parser.add_argument('--train-v2', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    report = build(args.index, args.validation_decisions, args.small_results,
                   args.validation_diagnostics, args.train_v1, args.train_v2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output':str(args.output), 'validation':report['validation'],
                      'diagnostics':report['targeted_validation_error_diagnostics'],
                      'train_pilots':report['training_prompt_development_pilots']}, indent=2))


if __name__ == '__main__':
    main()
