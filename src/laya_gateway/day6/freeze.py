"""Audit pre-test coverage without reading hidden references or unlocking test execution."""

import argparse
import json
from pathlib import Path

from .common import digest, read_json, write_new

TIERS = ('small', 'medium', 'frontier')
REQUIRED = ('model_identities', 'tokenizer_identities', 'generation_settings',
            'router_artifact', 'router_preprocessing', 'laya_gateway_questions',
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
    model_settings = {tier: set() for tier in TIERS}
    templates = {tier: {} for tier in TIERS}
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
                tier = row['tier']
                model_settings[tier].add((row.get('model'), row.get('model_revision'),
                                          row.get('settings_fingerprint')))
                task_templates = templates[tier].setdefault(row.get('task'), set())
                task_templates.add(row.get('template_fingerprint'))
    needed = {f'{split}/{tier}': len(split_ids[split]) for split in ('train', 'validation') for tier in TIERS}
    observed = {key: len(coverage[tuple(key.split('/'))]) for key in needed}
    short = [key for key in needed if observed[key] < needed[key]]
    identity_issues = []
    for tier in TIERS:
        observed_templates = {task: next(iter(values)) for task, values in templates[tier].items()
                              if len(values) == 1}
        if len(model_settings[tier]) > 1 or any(len(values) > 1 for values in templates[tier].values()):
            identity_issues.append(f'{tier}: mixed model, settings, or template identities')
        if len(model_settings[tier]) == 1:
            model, revision, settings = next(iter(model_settings[tier]))
            if config.get('model_identities') and \
               config['model_identities'].get(tier) != {'model': model, 'revision': revision}:
                identity_issues.append(f'{tier}: records disagree with freeze configuration')
            expected_settings = (config.get('generation_settings') or {}).get(tier)
            if expected_settings:
                mismatch = expected_settings.get('fingerprint') != settings
                if 'templates' in expected_settings:
                    mismatch = mismatch or expected_settings['templates'] != observed_templates
                elif len(observed_templates) == 1:
                    mismatch = mismatch or expected_settings.get('template') != next(iter(observed_templates.values()))
                else:
                    identity_issues.append(f'{tier}: task-scoped templates required in freeze configuration')
                    mismatch = False
                if mismatch:
                    identity_issues.append(f'{tier}: records disagree with freeze configuration')
    return {'schema': 'laya.day6.freeze_audit.v1', 'manifest_sha256': digest(manifest),
            'freeze_config_sha256': digest(freeze_config), 'result_sha256': [digest(p) for p in results],
            'manifest_counts': {split: len(ids) for split, ids in split_ids.items()},
            'required_scored_observations': needed, 'scored_observations': observed,
            'missing_freeze_fields': missing, 'coverage_shortfalls': short,
            'identity_issues': identity_issues,
            'incompatible_records': sorted(set(incompatible)),
            'ready_for_test': not (missing or short or incompatible or identity_issues)}


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
