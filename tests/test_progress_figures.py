"""Offline checks for the progress-figure data loaders (no plotting stack needed)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('make_progress_figures', ROOT / 'scripts' / 'make_progress_figures.py')
figs = module_from_spec(spec)
spec.loader.exec_module(figs)


def test_sources_are_committed_evidence_not_private_runs():
    for rel in figs.SOURCES.values():
        assert not rel.startswith('runs/'), rel
        assert (ROOT / rel).is_file(), rel
    for _, rel in figs.FULL_SUITE_RUNS:
        assert (ROOT / rel).is_file(), rel


def test_tier_outcomes_account_for_every_prompt():
    data = figs.tier_task_outcomes()
    expected_totals = {'train': {'math': 660, 'choice': 600, 'code': 240},
                       'validation': {'math': 220, 'choice': 200, 'code': 80}}
    for split, tiers in data.items():
        for tier, tasks in tiers.items():
            for task, row in tasks.items():
                assert row['total'] == expected_totals[split][task]
                assert sum(row[o] for o in figs.OUTCOMES) == row['total']
    assert sum(r['correct'] for r in data['validation']['small'].values()) == 324
    assert sum(r['correct'] for r in data['validation']['medium'].values()) == 402
    assert data['train']['small']['code']['other_error'] == 2  # one backend, one sandbox timeout


def test_paired_transitions_match_bootstrap_cohort():
    trans = figs.paired_transitions()
    rows = figs.bootstrap_intervals()
    assert sum(sum(t.values()) for t in trans.values()) == rows[0]['n'] == 476
    for row in rows:
        lo, hi = row['ci95']
        assert lo <= row['mean'] <= hi


def test_policy_replay_never_imputes_missing_results():
    rows = {r['label']: r for r in figs.policy_replay()}
    assert rows['Always frontier']['missing'] == 500 and rows['Always frontier']['correct'] == 0
    assert rows['Seeded random (seed 17)']['missing'] == 170
    v4, small = rows['Prompted-small router v4'], rows['Always small (1.5B)']
    assert (v4['correct'], v4['incorrect'], v4['parse_error']) == (small['correct'], small['incorrect'],
                                                                   small['parse_error'])


def test_policy_replay_rejects_unaccounted_prompts(tmp_path, monkeypatch):
    import json
    import shutil
    for key in ('baselines', 'prompted_v4'):
        dest = tmp_path / figs.SOURCES[key]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / figs.SOURCES[key], dest)
    path = tmp_path / figs.SOURCES['baselines']
    data = json.loads(path.read_text())
    data['policies'][1]['scored'] += 1  # one more outcome than prompts exist
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        figs.policy_replay(tmp_path)


def test_freeze_gate_and_manifest_counts():
    gate = figs.freeze_gate()
    assert gate['ready'] is False
    assert {(r['split'], r['tier']) for r in gate['rows']} == {
        (s, t) for s in ('train', 'validation') for t in ('small', 'medium', 'frontier')}
    assert all(r['scored'] <= r['required'] for r in gate['rows'])
    counts = figs.manifest_counts()
    assert {s: sum(c.values()) for s, c in counts.items()} == {'train': 1500, 'validation': 500, 'test': 500}


def test_test_history_is_parsed_from_saved_outputs():
    history = figs.test_history()
    assert history[0] == ('2026-10-27', 15)
    assert [d for d, _ in history] == sorted(d for d, _ in history)
