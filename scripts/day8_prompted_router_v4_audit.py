"""Summarize prompted-small v4 decisions without exposing prompt or response text."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)] if ordered else None


def summarize(decisions, expected_split, index, small_results=None):
    rows = read_jsonl(decisions)
    ids = [row.get('prompt_id') or row.get('selection', {}).get('prompt_id') for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f'duplicate prompt ID in {decisions}')
    if any(pid not in index or index[pid]['split'] != expected_split for pid in ids):
        raise ValueError(f'decisions in {decisions} do not match {expected_split} split')
    if any(row.get('version') != '4' for row in rows):
        raise ValueError(f'non-v4 row in {decisions}')

    by_task, tiers, errors = Counter(), Counter(), Counter()
    latencies, usage = [], Counter()
    outcomes = Counter()
    result_index = {}
    if small_results:
        result_index = {row['prompt_id']: row for row in read_jsonl(small_results)
                        if row['split'] == 'validation' and row['tier'] == 'small'}
    for row, prompt_id in zip(rows, ids):
        task = index[prompt_id]['task']
        if row['status'] == 'selected':
            selection = row['selection']
            tiers[selection['tier']] += 1
            by_task[f'{task}/selected'] += 1
            latencies.append(selection['decision_duration_ms'])
            usage.update(row.get('usage', {}))
            if small_results:
                saved = result_index.get(prompt_id) if selection['tier'] == 'small' else None
                outcomes[saved['outcome'] if saved else 'missing_saved_result'] += 1
        else:
            errors[f"{row.get('error_category')}/{row.get('cause_category')}"] += 1
            by_task[f'{task}/error'] += 1
    return {
        'expected_split': expected_split,
        'attempted': len(rows), 'selected': sum(tiers.values()),
        'selected_tiers': dict(tiers), 'errors': dict(errors),
        'decisions_by_task': dict(by_task),
        'saved_small_generator_outcomes_for_selected_prompts': dict(outcomes),
        'decision_duration_ms': {'n': len(latencies), 'median': percentile(latencies, .5),
                                 'p95': percentile(latencies, .95)},
        'usage_on_selected_decisions_only': dict(usage),
        'outcome_join_note': 'Matched saved generator outcomes; this router run made no generation requests.'
    }


def build(index_path, train_path, validation_path, small_path, failed_validation_path):
    index = {row['prompt_id']: row for row in read_jsonl(index_path)}
    if len(read_jsonl(index_path)) != len(index):
        raise ValueError('manifest index contains duplicate prompt IDs')
    train = summarize(train_path, 'train', index)
    validation = summarize(validation_path, 'validation', index, small_path)
    failed_validation = read_jsonl(failed_validation_path)
    failed_errors = Counter(
        f"{row.get('error_category')}/{row.get('cause_category')}"
        for row in failed_validation if row['status'] == 'error')
    if validation['attempted'] != 500:
        raise ValueError('expected exactly 500 validation decisions')
    return {
        'run_id': 'prompted-small-v4-20261120',
        'prompt_version': '4',
        'train_pilot': train,
        'validation': validation,
        'uncaptured_validation_attempt': {
            'attempted': len(failed_validation), 'errors': dict(failed_errors),
            'note': 'All rows failed to connect in the restricted shell. A later elevated inference invocation hit an existing output path and has no saved response records.'
        },
        'input_sha256': {str(path): sha256(path) for path in
                         (index_path, train_path, validation_path, small_path,
                          failed_validation_path)},
        'limits': [
            'The 30-prompt train pilot is development evidence and has no validation claim.',
            'Saved small-tier scores are joined descriptively; the router made no answer-generation calls.',
            'This is a local prompted-router comparison, not a Laya, DistilBERT, frontier, paid-provider, or held-out test result.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=Path('docs/day2-manifest-index.jsonl'))
    parser.add_argument('--train-decisions', type=Path, required=True)
    parser.add_argument('--validation-decisions', type=Path, required=True)
    parser.add_argument('--small-results', type=Path, required=True)
    parser.add_argument('--failed-validation-attempt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    report = build(args.index, args.train_decisions, args.validation_decisions,
                   args.small_results, args.failed_validation_attempt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(args.output), 'train_pilot': report['train_pilot'],
                      'validation': report['validation'],
                      'uncaptured_validation_attempt': report['uncaptured_validation_attempt']}, indent=2))


if __name__ == '__main__':
    main()
