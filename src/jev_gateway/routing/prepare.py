"""Export private development labels for classifier training and validation."""
import argparse
import json
from dataclasses import asdict
from pathlib import Path

from jev_gateway.evaluation.manifest import load
from jev_gateway.evaluation.records import Result
from .training_data import prepare_training, public_summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--run', type=Path, action='append', required=True)
    parser.add_argument('--split', choices=('train', 'validation'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('private label output must be under runs/')
    prompts = load(args.manifest, args.split)
    results = []
    for path in args.run:
        results.extend(Result.model_validate_json(line) for line in path.read_text().splitlines() if line)
    rows, report = prepare_training(prompts, results, args.split)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as out:
        for row in rows:
            out.write(json.dumps(asdict(row), sort_keys=True)+'\n')
    print(json.dumps(public_summary(rows, report), default=list, sort_keys=True))


if __name__ == '__main__':
    main()
