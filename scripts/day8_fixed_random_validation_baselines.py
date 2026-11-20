"""Replay fixed and seeded-random baselines on saved local validation outcomes."""
import argparse
import hashlib
import json
from pathlib import Path

from jev_gateway.evaluation.manifest import load
from jev_gateway.evaluation.records import Result
from jev_gateway.routing.comparison import baselines, compare


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_results(path):
    return [Result.model_validate_json(line) for line in path.read_text().splitlines() if line]


def build(manifest, small_path, medium_math_choice, medium_code, rescore, *, seed=17):
    prompts = load(manifest, 'validation')
    results = _read_results(small_path) + _read_results(medium_math_choice) + _read_results(medium_code)
    rescore_data = json.loads(rescore.read_text())
    if rescore_data['source_prompt_id'] != 'mbpp:401' or \
       rescore_data['corrected_classification']['outcome'] != 'incorrect':
        raise ValueError('unexpected MBPP reclassification evidence')
    revised = []
    override_count = 0
    for result in results:
        if result.prompt_id == 'mbpp:401' and result.tier == 'medium':
            result = result.model_copy(update={'outcome':'incorrect', 'score':0.0,
                                               'error_category':'crashed'})
            override_count += 1
        revised.append(result)
    if override_count != 1:
        raise ValueError(f'expected one medium mbpp:401 result, found {override_count}')
    results = revised
    selections = baselines(prompts, seed=seed)
    reports = compare(prompts, results, selections)
    return {
        'run_id': 'medium-validation-fixed-random-baselines-20261120',
        'split': 'validation', 'expected_prompt_count': len(prompts),
        'policies': reports, 'seed': seed,
        'classification_override': {
            'prompt_id': 'mbpp:401', 'tier': 'medium',
            'outcome': 'incorrect', 'score': 0.0,
            'source': str(rescore), 'source_sha256': _sha256(rescore)
        },
        'input_sources': {str(path): _sha256(path) for path in
                          (manifest, small_path, medium_math_choice, medium_code)},
        'limits': [
            'Only fixed-tier and seeded-random baselines are replayed; no Jev, prompted-router, or frontier decision was observed.',
            'Missing frontier outputs reduce seeded-random coverage; no missing result is imputed.',
            'Provider charges are unknown, so no cost frontier or cost-quality claim is made.',
            'Validation results are descriptive and do not select a threshold or use the held-out test.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--small', type=Path, default=Path('runs/day2-run-ddd52bb7b6c74b15b68a1df581e8ba1b.jsonl'))
    parser.add_argument('--medium-math-choice', type=Path,
                        default=Path('runs/day2-run-1024c23932c74897a9c95604c7f88836.jsonl'))
    parser.add_argument('--medium-code', type=Path,
                        default=Path('runs/day2-run-66afe463970d4f04900c50c204c1510f.jsonl'))
    parser.add_argument('--rescore', type=Path,
                        default=Path('evidence/day8/medium-validation-code-mbpp401-rescore-20261120.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=17)
    args = parser.parse_args(argv)
    report = build(args.manifest, args.small, args.medium_math_choice,
                   args.medium_code, args.rescore, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output':str(args.output), 'policies':report['policies']}, indent=2))


if __name__ == '__main__':
    main()
