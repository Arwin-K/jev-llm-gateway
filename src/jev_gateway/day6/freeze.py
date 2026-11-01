"""Audit pre-test coverage without reading hidden references or unlocking test execution."""

import argparse
import json
from pathlib import Path

from .common import digest, read_json, write_new

TIERS = ('small', 'medium', 'frontier')
REQUIRED = ('model_identities', 'tokenizer_identities', 'generation_settings',
            'router_artifact', 'router_preprocessing', 'jev_questions',
            'backend_descriptions', 'thresholds', 'fallback_rules',
            'scoring_rules', 'source_revision')


def audit(manifest: Path, results: list[Path], freeze_config: Path) -> dict:
    config = read_json(freeze_config)
    missing = [key for key in REQUIRED if not config.get(key)]
    split_ids = {'train': set(), 'validation': set(), 'test': set()}
    for line in manifest.read_text().splitlines():
        row = json.loads(line)
        split_ids[row['split']].add(row['prompt_id'])
    coverage = {(split, tier): set() for split in ('train', 'validation') for tier in TIERS}
    incompatible = []
    for path in results:
        for line in path.read_text().splitlines():
            row = json.loads(line)
            split = row.get('split')
            if split == 'test':
                incompatible.append('test result exists before freeze')
                continue
            if split not in ('train', 'validation') or row.get('prompt_id') not in split_ids[split]:
                incompatible.append('unknown prompt or split')
                continue
            if row.get('tier') not in TIERS or row.get('execution') != 'real':
                incompatible.append('unknown tier or nonreal observation')
                continue
            if row.get('score') is not None and row.get('outcome') in ('correct', 'incorrect'):
                coverage[(split, row['tier'])].add(row['prompt_id'])
    needed = {f'{split}/{tier}': len(split_ids[split]) for split in ('train', 'validation') for tier in TIERS}
    observed = {key: len(coverage[tuple(key.split('/'))]) for key in needed}
    short = [key for key in needed if observed[key] < needed[key]]
    return {'schema': 'jev.day6.freeze_audit.v1', 'manifest_sha256': digest(manifest),
            'freeze_config_sha256': digest(freeze_config), 'result_sha256': [digest(p) for p in results],
            'manifest_counts': {split: len(ids) for split, ids in split_ids.items()},
            'required_scored_observations': needed, 'scored_observations': observed,
            'missing_freeze_fields': missing, 'coverage_shortfalls': short,
            'incompatible_records': sorted(set(incompatible)),
            'ready_for_test': not (missing or short or incompatible)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--results', type=Path, action='append', required=True)
    parser.add_argument('--freeze-config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    write_new(args.output, audit(args.manifest, args.results, args.freeze_config))


if __name__ == '__main__':
    main()
