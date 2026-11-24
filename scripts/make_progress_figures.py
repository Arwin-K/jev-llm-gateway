"""Regenerate the project progress figures from committed, sanitized evidence.

Every chart reads only files tracked in this repository (``evidence/`` audits,
the metadata-only manifest index, saved pytest output, and ``git log``).  Raw
model answers under ignored ``runs/`` are never read, so anyone with a clean
checkout can rebuild identical figures.

Data loading is stdlib-only so the offline test suite can check it without a
plotting stack.  Drawing needs matplotlib from ``requirements/figures.txt``::

    make setup-figures
    make figures                      # writes docs/figures/progress/*.svg
    .venv-figures/bin/python scripts/make_progress_figures.py --png-dir /tmp/png
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / 'docs' / 'figures' / 'progress'

SOURCES = {
    'small_train': 'evidence/day7/small-train-full-audit-20261119.json',
    'small_validation': 'evidence/day7/local-v2-coverage-audit-20261114.json',
    'medium_train': 'evidence/day8/medium-train-full-audit-20261120.json',
    'medium_validation': 'evidence/day8/medium-validation-full-audit-reclassified-20261120.json',
    'bootstrap': 'evidence/day8/medium-validation-paired-group-bootstrap-20261120.json',
    'baselines': 'evidence/day8/medium-validation-fixed-random-baselines-20261120.json',
    'prompted_v4': 'evidence/day8/prompted-small-v4-audit-20261120.json',
    'freeze': 'evidence/day8/freeze-audit-after-mbpp401-rescore-20261120.json',
    'manifest_index': 'docs/day2-manifest-index.jsonl',
}

# Full offline-suite outputs only (focused runs are excluded); date = run day.
FULL_SUITE_RUNS = [
    ('2026-10-27', 'evidence/day1/mac-offline-20261027-1314.txt'),
    ('2026-10-29', 'evidence/day3/mac-offline-20261029-followup.txt'),
    ('2026-10-30', 'evidence/day4/mac-offline-20261030-1838.txt'),
    ('2026-10-31', 'evidence/day5/mac-offline-20261031.txt'),
    ('2026-11-01', 'evidence/day6/mac-offline-final-20261101.txt'),
    ('2026-11-16', 'evidence/testing/offline-suite-20261116.txt'),
    ('2026-11-17', 'evidence/testing/maintenance-offline-20261117.txt'),
    ('2026-11-19', 'evidence/testing/offline-after-prompt-id-filter-20261119T2246-0500.txt'),
    ('2026-11-20', 'evidence/testing/offline-suite-day8-post-v4-20261120.txt'),
    ('2026-11-21', 'evidence/testing/offline-suite-day9-post-cleanup-20261121.txt'),
]

TASKS = ('math', 'choice', 'code')
TASK_LABEL = {'math': 'Math (GSM8K)', 'choice': 'Choice (MMLU)', 'code': 'Code (MBPP)'}
OUTCOMES = ('correct', 'incorrect', 'parse_error', 'other_error')


def _load(rel: str, root: Path = ROOT):
    return json.loads((root / rel).read_text())


# ---------------------------------------------------------------- data loaders


def _normalize(counts: dict) -> dict:
    """Fold any backend/evaluator failure keys into ``other_error``."""
    out = {'total': counts['total'], 'correct': counts.get('correct', 0),
           'incorrect': counts.get('incorrect', 0), 'parse_error': counts.get('parse_error', 0)}
    out['other_error'] = out['total'] - out['correct'] - out['incorrect'] - out['parse_error']
    if out['other_error'] < 0:
        raise ValueError(f'outcome counts exceed total: {counts}')
    return out


def tier_task_outcomes(root: Path = ROOT) -> dict:
    """{split: {tier: {task: {total, correct, incorrect, parse_error, other_error}}}}."""
    small_val = _load(SOURCES['small_validation'], root)['observations']['small_validation']
    raw = {
        'train': {
            'small': _load(SOURCES['small_train'], root)['task_outcomes'],
            'medium': _load(SOURCES['medium_train'], root)['task_outcomes'],
        },
        'validation': {
            'small': small_val['task_counts'],
            'medium': _load(SOURCES['medium_validation'], root)['task_outcomes'],
        },
    }
    return {split: {tier: {task: _normalize(t[task]) for task in TASKS} for tier, t in tiers.items()}
            for split, tiers in raw.items()}


def paired_transitions(root: Path = ROOT) -> dict:
    """Validation prompts scored binary by both tiers: {task: transition counts}."""
    by_task = _load(SOURCES['bootstrap'], root)['by_task']
    return {task: dict(by_task[task]['transitions']) for task in TASKS}


def bootstrap_intervals(root: Path = ROOT) -> list[dict]:
    data = _load(SOURCES['bootstrap'], root)
    rows = [{'label': 'All tasks', 'n': data['overall']['prompt_count'],
             'mean': data['overall']['mean_right_minus_left'], 'ci95': data['overall']['ci95']}]
    for task in TASKS:
        t = data['by_task'][task]
        rows.append({'label': TASK_LABEL[task], 'n': t['prompt_count'],
                     'mean': t['mean_right_minus_left'], 'ci95': t['ci95']})
    meta = {'seed': data['seed'], 'repetitions': data['repetitions']}
    return [dict(r, **meta) for r in rows]


def policy_replay(root: Path = ROOT) -> list[dict]:
    """Validation policies over all 500 expected prompts, with nothing imputed."""
    base = {p['policy']: p for p in _load(SOURCES['baselines'], root)['policies']}
    rows = []
    for name, label in [('always-small', 'Always small (1.5B)'),
                        ('seeded-random-17', 'Seeded random (seed 17)'),
                        ('always-medium', 'Always medium (7B)'),
                        ('always-frontier', 'Always frontier')]:
        p = base[name]
        rows.append({'label': label, 'expected': p['expected'], 'correct': p['correct'],
                     'incorrect': p['scored'] - p['correct'], 'parse_error': p['parse_errors'],
                     'missing': p['missing_result'] + p['failed_result']})
    v4 = _load(SOURCES['prompted_v4'], root)['validation']
    joined = v4['saved_small_generator_outcomes_for_selected_prompts']
    rows.insert(1, {'label': 'Prompted-small router v4', 'expected': v4['attempted'],
                    'correct': joined.get('correct', 0), 'incorrect': joined.get('incorrect', 0),
                    'parse_error': joined.get('parse_error', 0),
                    'missing': v4['attempted'] - v4['selected'],
                    'note': f"selected small on {v4['selected_tiers'].get('small', 0)}/{v4['attempted']}"})
    for r in rows:
        if r['correct'] + r['incorrect'] + r['parse_error'] + r['missing'] != r['expected']:
            raise ValueError(f'policy row does not account for every prompt: {r}')
    return rows


def latency_quality(root: Path = ROOT) -> dict:
    med = _load(SOURCES['medium_validation'], root)
    durations = med['small_vs_medium_result_duration_seconds']
    small_val = _load(SOURCES['small_validation'], root)['observations']['small_validation']
    v4 = _load(SOURCES['prompted_v4'], root)['validation']['decision_duration_ms']
    return {
        'small': dict(durations['small'], correct=small_val['outcomes']['correct'], total=small_val['unique_prompts']),
        'medium': dict(durations['medium'], correct=med['aggregate_outcomes']['correct'], total=med['prompt_ids_observed']),
        'router_decision_ms': v4,
    }


def freeze_gate(root: Path = ROOT) -> dict:
    data = _load(SOURCES['freeze'], root)
    rows = []
    for key, required in data['required_scored_observations'].items():
        split, tier = key.split('/')
        rows.append({'split': split, 'tier': tier, 'scored': data['scored_observations'].get(key, 0),
                     'required': required})
    order = {'small': 0, 'medium': 1, 'frontier': 2}
    rows.sort(key=lambda r: (r['split'] != 'train', order[r['tier']]))
    return {'rows': rows, 'missing_fields': list(data['missing_freeze_fields']),
            'identity_issues': len(data['identity_issues']), 'ready': bool(data['ready_for_test']),
            'manifest_counts': data['manifest_counts']}


def manifest_counts(root: Path = ROOT) -> dict:
    """{split: {task: count}} from the metadata-only index (no prompt text)."""
    counts: dict = defaultdict(Counter)
    for line in (root / SOURCES['manifest_index']).read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            counts[row['split']][row['task']] += 1
    return {split: dict(c) for split, c in counts.items()}


def test_history(root: Path = ROOT) -> list[tuple[str, int]]:
    out = []
    for day, rel in FULL_SUITE_RUNS:
        found = re.findall(r'(\d+) passed', (root / rel).read_text())
        if not found:
            raise ValueError(f'no pytest pass count in {rel}')
        out.append((day, max(int(n) for n in found)))
    return out


def commits_per_day(root: Path = ROOT) -> list[tuple[str, int]]:
    """Commits per America/Toronto calendar day from the local git history."""
    try:
        text = subprocess.run(
            ['git', 'log', '--date=format-local:%Y-%m-%d', '--pretty=%ad'],
            cwd=root, check=True, capture_output=True, text=True,
            env={'TZ': 'America/Toronto', 'PATH': '/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin'},
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return sorted(Counter(text.split()).items())


# ---------------------------------------------------------------- drawing

COLORS = {
    'small': '#3D7CC9', 'medium': '#23966B', 'frontier': '#9AA3AE',
    'correct': '#2F8F67', 'incorrect': '#D2604F', 'parse_error': '#E8B04B',
    'other_error': '#8C6BB8', 'missing': '#E3E6EA',
    'both_correct': '#8CBDEB', 'medium_only': '#F2A541', 'small_only': '#B48EE0', 'both_wrong': '#6B7280',
    'ink': '#1F2933', 'muted': '#66727F', 'grid': '#E6E9ED', 'panel': '#F6F8FA',
    'live': '#23966B', 'offline': '#3D7CC9', 'pending': '#9AA3AE', 'locked': '#C0392B',
}
OUTCOME_LABEL = {'correct': 'Correct', 'incorrect': 'Incorrect', 'parse_error': 'Parse error',
                 'other_error': 'Backend/evaluator error', 'missing': 'No result (not run)'}


def _setup():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': COLORS['grid'],
        'axes.labelcolor': COLORS['ink'], 'xtick.color': COLORS['muted'], 'ytick.color': COLORS['ink'],
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold',
        'axes.titlesize': 13, 'axes.titlelocation': 'left', 'svg.hashsalt': 'laya-progress-figures',
        'svg.fonttype': 'path', 'figure.facecolor': 'white',
    })
    return plt


def _header(fig, title: str, subtitle: str, source: str):
    import textwrap
    width_in = fig.get_figwidth()
    fig.text(0.03, 0.965, title, fontsize=17, fontweight='bold', color=COLORS['ink'], va='top')
    fig.text(0.03, 0.915, textwrap.fill(subtitle, int(width_in * 0.94 * 10.5)), fontsize=11.5,
             color=COLORS['muted'], va='top', linespacing=1.35)
    fig.text(0.03, 0.015, textwrap.fill(f'Source: {source}', int(width_in * 0.94 * 14.5)), fontsize=8.5,
             color=COLORS['muted'], va='bottom')


def _save(fig, name: str, out: Path, png_dir: Path | None, written: list):
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'{name}.svg'
    fig.savefig(path, format='svg', metadata={'Date': None})
    written.append(path)
    if png_dir:
        png_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(png_dir / f'{name}.png', format='png', dpi=200)
    import matplotlib.pyplot as plt
    plt.close(fig)


ROW_H = 2.7


def _box(ax, x, top, w, title, items=(), status=None, title_color=None, dashed=False):
    """Draw a titled box whose height fits its status-dotted items; return its bottom y."""
    from matplotlib.patches import FancyBboxPatch
    h = 6.2 + max(len(items) - 1, 0) * ROW_H + 2.8 if items else 6.0
    y = top - h
    edge = COLORS.get(status, '#C9CFD6') if status else '#C9CFD6'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.2',
                                linewidth=1.8, edgecolor=edge, facecolor='white',
                                linestyle=(0, (4, 3)) if dashed else '-', zorder=2))
    ax.text(x + w / 2, top - 2.0, title, ha='center', va='top', fontsize=11.5, fontweight='bold',
            color=title_color or COLORS['ink'], zorder=3)
    for i, (label, st) in enumerate(items):
        yy = top - 6.2 - i * ROW_H
        ax.scatter([x + 1.6], [yy], s=38, color=COLORS[st], zorder=4, edgecolors='white', linewidths=0.6)
        ax.text(x + 3.0, yy, label, ha='left', va='center', fontsize=9.2, color=COLORS['ink'], zorder=4)
    return y


def _arrow(ax, x0, y0, x1, y1, label=None, color=None):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=1,
                arrowprops=dict(arrowstyle='-|>', color=color or '#8A96A3', lw=1.6, mutation_scale=14))
    if label:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.4, label, ha='center', va='bottom', fontsize=8.5,
                color=COLORS['muted'])


def _status_legend(ax, x, y):
    for i, (st, label) in enumerate([('live', 'Ran live on the Mac (real evidence)'),
                                     ('offline', 'Implemented, verified with offline tests only'),
                                     ('pending', 'Blocked: needs credentials, artifact, or GPU')]):
        ax.scatter([x + i * 33], [y], s=60, color=COLORS[st], edgecolors='white')
        ax.text(x + i * 33 + 1.4, y, label, va='center', fontsize=9.5, color=COLORS['ink'])


def fig_system_map(plt, out, png_dir, written, root):
    lq = latency_quality(root)
    fig = plt.figure(figsize=(15, 9))
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.80])
    ax.set_xlim(0, 100), ax.set_ylim(0, 62), ax.axis('off')
    _header(fig, 'Laya gateway: what exists and what has actually run',
            'Request path (top) and the evaluation, deployment and monitoring stack around it. '
            'Dot colour = strongest evidence for that component.',
            'docs/FEATURE_STATUS.md, evidence/day5, evidence/day8, evidence/day9')

    _box(ax, 0.5, 49, 11, 'Client', [('OpenAI-style', 'live'), ('chat request', 'live')])
    _box(ax, 14, 54, 16.5, 'FastAPI gateway', [
        ('explicit tiers + auto', 'live'), ('SSE streaming', 'offline'), ('deadlines + traces', 'offline'),
        ('request/token/USD caps', 'offline'), ('circuit breaker', 'offline'), ('live smoke: HTTP 200', 'live')])
    _box(ax, 33.5, 54, 15, 'Semantic cache', [
        ('MiniLM embeddings', 'pending'), ('FAISS index', 'pending'), ('scope + freshness', 'offline'),
        ('Laya reuse check', 'offline'), ('verified answers only', 'offline')])
    _box(ax, 51.5, 54, 17.5, 'Router (model=auto)', [
        ('Laya choice/success', 'pending'), ('DistilBERT fallback', 'pending'),
        (f"prompted-small v4 ({lq['router_decision_ms']['median']:.0f} ms)", 'live'),
        ('Strands decider', 'pending'), ('fixed / random', 'live'), ('JSON-schema output', 'live'),
        ('eligibility gates', 'offline')])
    _box(ax, 72, 54, 12, 'small tier', [('qwen2.5:1.5b', 'live')], status='live')
    _box(ax, 72, 43.5, 12, 'medium tier', [('qwen2.5:7b', 'live')], status='live')
    _box(ax, 72, 33, 12, 'frontier tier', [('paid API, capped', 'pending')], status='pending', dashed=True)
    _box(ax, 87, 54, 12.5, 'Laya verifier', [
        ('accept / reject', 'offline'), ('escalate: small →', 'offline'), ('medium → frontier', 'offline'),
        ('accepted → cache', 'offline'), ('live Laya API', 'pending')])

    _arrow(ax, 11.8, 43, 13.7, 43)
    _arrow(ax, 30.8, 46, 33.2, 46)
    _arrow(ax, 48.8, 46, 51.2, 46)
    for yy in (49.5, 39, 28.5):
        _arrow(ax, 69.3, 42, 71.7, yy)
        _arrow(ax, 84.3, yy, 86.7, 44)

    _box(ax, 0.5, 19, 30, 'Evaluation harness', [
        ('2,500-prompt frozen manifest', 'live'), ('Docker code sandbox (no network)', 'live'),
        ('bootstrap, replay, freeze audit', 'live'), ('held-out test: locked', 'pending')])
    _box(ax, 33.5, 19, 20, 'Deployment', [
        ('ARM Docker image', 'live'), ('Compose profile', 'live'), ('kind k8s, 2 pods', 'live'),
        ('Colab vLLM notebook', 'pending')])
    _box(ax, 56.5, 19, 20, 'Observability', [
        ('Prometheus scrape up', 'live'), ('Grafana: 14 panels', 'live'), ('17 PromQL checks', 'live'),
        ('real-traffic dashboards', 'pending')])
    _box(ax, 79.5, 19, 20, 'Load + CI', [
        ('Locust steady/spike/soak', 'offline'), ('2-request wiring check', 'live'),
        ('make verify: 167 tests', 'live'), ('remote CI run', 'pending')])
    _status_legend(ax, 2, 60.5)
    _save(fig, '01-system-map', out, png_dir, written)


def fig_eval_pipeline(plt, out, png_dir, written, root):
    counts = manifest_counts(root)
    freeze = freeze_gate(root)
    fig = plt.figure(figsize=(15, 7.6))
    ax = fig.add_axes([0.02, 0.07, 0.96, 0.78])
    ax.set_xlim(0, 100), ax.set_ylim(0, 50), ax.axis('off')
    _header(fig, 'How a model answer becomes evidence',
            'Pinned datasets → frozen split → capped evaluation runs → isolated scoring → immutable records → sanitized audits.',
            f"{SOURCES['manifest_index']}, {SOURCES['freeze']}, docs/DAY2_DATASETS.md")

    def split_label(split):
        c = counts.get(split, {})
        return f"{split} {sum(c.values()):,} · " + '/'.join(str(c.get(t, 0)) for t in TASKS)

    total = sum(sum(c.values()) for c in counts.values())
    _box(ax, 0.5, 44, 15, 'Pinned sources', [('GSM8K (openai/gsm8k)', 'live'), ('MMLU (cais/mmlu)', 'live'),
                                             ('MBPP sanitized', 'live'), ('revision-pinned', 'live'),
                                             ('prompt text private', 'live')])
    _box(ax, 18, 44, 17.5, f'Frozen manifest · {total:,}', [
        (split_label('train'), 'live'), (split_label('validation'), 'live'),
        (split_label('test') + ' (locked)', 'pending'), ('seeded 60/20/20, group-aware', 'live')])
    ax.text(26.75, 25.6, 'counts: math / choice / code', ha='center', fontsize=8.5, color=COLORS['muted'])
    _box(ax, 38, 44, 15, 'laya eval-run', [('request + token caps', 'live'), ('concurrency 1, no retry', 'live'),
                                          ('resumable checkpoints', 'live'), ('--task / --prompt-id', 'live'),
                                          ('output path reserved', 'live'), ('paid tiers gated', 'offline')])
    _box(ax, 55.5, 44, 15, 'Scorers', [('math: strict final', 'live'), ('number parser', 'live'),
                                       ('choice: A–D', 'live'), ('code: Docker sandbox', 'live'),
                                       ('no net, 256 MB, 1 CPU', 'live'), ('SyntaxError → incorrect', 'live')])
    _box(ax, 73, 44, 12, 'Run records', [('immutable JSONL', 'live'), ('fingerprints', 'live'),
                                         ('SHA-256 inputs', 'live'), ('raw stays private', 'live')])
    audits_bottom = _box(ax, 87.5, 44, 12, 'Sanitized audits', [
        ('tier outcomes', 'live'), ('paired bootstrap', 'live'), ('policy replay', 'live'),
        ('router audit', 'live'), ('freeze gate', 'live')])
    _box(ax, 38, 15.5, 61.5, 'Freeze gate before any held-out evaluation', [
        (f"identity issues: {freeze['identity_issues']}", 'live'),
        (f"missing freeze fields: {len(freeze['missing_fields'])}", 'pending'),
        (f"ready_for_test = {str(freeze['ready']).lower()}  →  test split stays locked", 'pending')],
        status='locked', title_color=COLORS['locked'])
    for x0, x1 in ((15.8, 17.7), (35.8, 37.7), (53.3, 55.2), (70.8, 72.7), (85.3, 87.2)):
        _arrow(ax, x0, 36, x1, 36)
    _arrow(ax, 93.5, audits_bottom - 0.4, 93.5, 15.9)
    ax.annotate('', xy=(26.75, 24.6), xytext=(37.7, 8), zorder=1,
                arrowprops=dict(arrowstyle='-|>', color=COLORS['locked'], lw=1.4, ls='--', mutation_scale=13))
    ax.text(29.5, 13, 'test opens only\nwhen ready', fontsize=8.5, color=COLORS['locked'], ha='center')
    _status_legend(ax, 2, 48.8)
    _save(fig, '02-evaluation-pipeline', out, png_dir, written)


def fig_tier_outcomes(plt, out, png_dir, written, root):
    data = tier_task_outcomes(root)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8), sharey=True)
    fig.subplots_adjust(left=0.15, right=0.98, top=0.78, bottom=0.2, wspace=0.06)
    _header(fig, 'Medium (7B) beats small (1.5B) on every task; small is already strong on math',
            'Share of prompts by outcome. Every prompt is counted; parse and runtime failures are shown, not dropped.',
            ', '.join(SOURCES[k] for k in ('small_train', 'medium_train', 'small_validation', 'medium_validation')))
    labels, ypos = [], []
    for i, task in enumerate(TASKS):
        for j, tier in enumerate(('small', 'medium')):
            ypos.append(i * 2.6 + j)
            labels.append(f"{TASK_LABEL[task]}\n{'1.5B small' if tier == 'small' else '7B medium'}")
    for ax, split in zip(axes, ('train', 'validation')):
        y = 0
        for i, task in enumerate(TASKS):
            for j, tier in enumerate(('small', 'medium')):
                row = data[split][tier][task]
                left = 0.0
                yy = ypos[y]
                for oc in OUTCOMES:
                    frac = row[oc] / row['total']
                    if frac:
                        ax.barh(yy, frac, left=left, height=0.82, color=COLORS[oc], edgecolor='white', lw=0.8)
                    left += frac
                acc = row['correct'] / row['total']
                ax.text(0.012, yy, f"{acc:.1%}", va='center', ha='left', color='white', fontsize=10.5, fontweight='bold')
                ax.text(1.01, yy, f"n={row['total']}", va='center', ha='left', color=COLORS['muted'], fontsize=9)
                y += 1
        total_correct = {t: sum(data[split][t][k]['correct'] for k in TASKS) for t in ('small', 'medium')}
        total_n = {t: sum(data[split][t][k]['total'] for k in TASKS) for t in ('small', 'medium')}
        ax.set_title(f"{split.capitalize()} split  ·  overall correct: small {total_correct['small']}/{total_n['small']}"
                     f", medium {total_correct['medium']}/{total_n['medium']}", fontsize=11.5, pad=10)
        ax.set_xlim(0, 1.09)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ['0%', '25%', '50%', '75%', '100%'])
        ax.xaxis.grid(True, color=COLORS['grid']), ax.set_axisbelow(True)
        ax.spines['left'].set_visible(False), ax.tick_params(axis='y', length=0)
    axes[0].set_yticks(ypos, labels, fontsize=9.5)
    axes[0].invert_yaxis()
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[o]) for o in OUTCOMES]
    fig.legend(handles, [OUTCOME_LABEL[o] for o in OUTCOMES], loc='lower center', ncol=4, frameon=False,
               bbox_to_anchor=(0.56, 0.075), fontsize=10)
    _save(fig, '03-tier-outcomes', out, png_dir, written)


def fig_transitions(plt, out, png_dir, written, root):
    trans = paired_transitions(root)
    keys = [('both_correct', 'Both correct: small is enough', 'both_correct'),
            ('small_incorrect_medium_correct', 'Only 7B correct: escalate', 'medium_only'),
            ('small_correct_medium_incorrect', 'Only 1.5B correct', 'small_only'),
            ('both_incorrect', 'Both wrong: needs frontier or verifier', 'both_wrong')]
    rows = [('All tasks', {k: sum(trans[t][k] for t in TASKS) for k, _, _ in keys})]
    rows += [(TASK_LABEL[t], trans[t]) for t in TASKS]
    fig, ax = plt.subplots(figsize=(14, 6.2))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.76, bottom=0.2)
    total = sum(rows[0][1].values())
    escal = rows[0][1]['small_incorrect_medium_correct']
    _header(fig, 'Where a router could help: the same validation prompts answered by both tiers',
            f'{total} prompts scored correct/incorrect by both models. Only {escal} ({escal / total:.0%}) need the 7B '
            'and are fixed by it; a good router sends the rest to the 1.5B.',
            SOURCES['bootstrap'] + ' (paired binary transitions)')
    for i, (label, t) in enumerate(rows):
        n = sum(t.values())
        left = 0
        for k, _, c in keys:
            frac = t[k] / n
            ax.barh(i, frac, left=left, color=COLORS[c], edgecolor='white', height=0.72, lw=1)
            if frac > 0.025:
                ax.text(left + frac / 2, i, f"{t[k]}", ha='center', va='center', fontsize=10.5,
                        color='white' if c in ('both_wrong',) else COLORS['ink'], fontweight='bold')
            left += frac
        ax.text(1.008, i, f'n={n}', va='center', fontsize=9.5, color=COLORS['muted'])
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=11)
    ax.invert_yaxis(), ax.set_xlim(0, 1.06)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0%', '25%', '50%', '75%', '100%'])
    ax.spines['left'].set_visible(False), ax.tick_params(axis='y', length=0)
    ax.get_yticklabels()[0].set_fontweight('bold')
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[c]) for _, _, c in keys]
    fig.legend(handles, [lbl for _, lbl, _ in keys], loc='lower center', ncol=4, frameon=False,
               bbox_to_anchor=(0.55, 0.07), fontsize=10)
    _save(fig, '04-paired-transitions', out, png_dir, written)


def fig_bootstrap(plt, out, png_dir, written, root):
    rows = bootstrap_intervals(root)
    fig, ax = plt.subplots(figsize=(12, 5.6))
    fig.subplots_adjust(left=0.2, right=0.95, top=0.74, bottom=0.2)
    _header(fig, 'How much better is the 7B? Medium minus small accuracy, with 95% intervals',
            f"Paired group bootstrap on validation ({rows[0]['repetitions']:,} resamples, seed {rows[0]['seed']}). "
            'Every interval is above zero.', SOURCES['bootstrap'])
    for i, r in enumerate(rows):
        lo, hi = r['ci95']
        col = COLORS['ink'] if i == 0 else COLORS['medium']
        ax.plot([lo * 100, hi * 100], [i, i], color=col, lw=3.2 if i == 0 else 2.4, solid_capstyle='round')
        ax.scatter([r['mean'] * 100], [i], s=110 if i == 0 else 80, color=col, zorder=3, edgecolors='white', lw=1.5)
        ax.text(hi * 100 + 0.6, i, f"+{r['mean'] * 100:.1f} pp  [{lo * 100:+.1f}, {hi * 100:+.1f}]",
                va='center', fontsize=10, color=COLORS['ink'])
    ax.axvline(0, color=COLORS['muted'], lw=1, ls='--')
    ax.set_yticks(range(len(rows)), [f"{r['label']}  (n={r['n']})" for r in rows], fontsize=10.5)
    ax.get_yticklabels()[0].set_fontweight('bold')
    ax.invert_yaxis(), ax.set_xlim(-2, 36)
    ax.set_xlabel('accuracy difference, percentage points (7B − 1.5B)')
    ax.xaxis.grid(True, color=COLORS['grid']), ax.set_axisbelow(True)
    ax.spines['left'].set_visible(False), ax.tick_params(axis='y', length=0)
    fig.text(0.2, 0.065, 'Descriptive validation evidence only: not a routing threshold or a held-out estimate.',
             fontsize=9, color=COLORS['muted'])
    _save(fig, '05-paired-bootstrap', out, png_dir, written)


def fig_policies(plt, out, png_dir, written, root):
    rows = policy_replay(root)
    fig, ax = plt.subplots(figsize=(14, 6.2))
    fig.subplots_adjust(left=0.19, right=0.8, top=0.78, bottom=0.2)
    _header(fig, 'Routing policies replayed on 500 validation prompts',
            'Correct completions out of all expected prompts. Missing frontier answers stay missing; nothing is imputed.',
            f"{SOURCES['baselines']}, {SOURCES['prompted_v4']}")
    parts = ('correct', 'incorrect', 'parse_error', 'missing')
    for i, r in enumerate(rows):
        left = 0
        for p in parts:
            if r[p]:
                ax.barh(i, r[p], left=left, color=COLORS[p], edgecolor='white', height=0.7, lw=1,
                        hatch='///' if p == 'missing' else None)
            left += r[p]
        rate = r['correct'] / r['expected']
        txt = (f"{r['correct']}/{r['expected']}  ({rate:.1%})" if r['missing'] < r['expected']
               else 'no observations')
        if r.get('note'):
            txt += f"\n{r['note']}"
        ax.text(r['expected'] + 6, i, txt, va='center', fontsize=10, color=COLORS['ink'])
    ax.set_yticks(range(len(rows)), [r['label'] for r in rows], fontsize=10.5)
    ax.invert_yaxis(), ax.set_xlim(0, 500)
    ax.set_xlabel('validation prompts')
    ax.spines['left'].set_visible(False), ax.tick_params(axis='y', length=0)
    ax.text(250, len(rows) - 1, 'not run: frontier credentials and spending caps not configured',
            ha='center', va='center', fontsize=10, color=COLORS['muted'])
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[p], hatch='///' if p == 'missing' else None,
                             edgecolor='white') for p in parts]
    fig.legend(handles, [OUTCOME_LABEL[p] for p in parts], loc='lower center', ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.06), fontsize=10)
    _save(fig, '06-policy-replay', out, png_dir, written)


def fig_latency(plt, out, png_dir, written, root):
    lq = latency_quality(root)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.subplots_adjust(left=0.1, right=0.95, top=0.76, bottom=0.18)
    _header(fig, 'The quality/latency trade-off a router has to manage',
            'Validation, per-prompt evaluation duration: dot = median, bar = up to p95. '
            'Small rows come from earlier sessions, so this is not a same-session load benchmark.',
            SOURCES['medium_validation'] + ', ' + SOURCES['small_validation'])
    for tier in ('small', 'medium'):
        d = lq[tier]
        acc = d['correct'] / d['total'] * 100
        ax.plot([d['median'], d['p95']], [acc, acc], color=COLORS[tier], lw=3, alpha=0.45, solid_capstyle='round')
        ax.scatter([d['median']], [acc], s=260, color=COLORS[tier], zorder=3, edgecolors='white', lw=2)
        name = 'qwen2.5:1.5b (small)' if tier == 'small' else 'qwen2.5:7b (medium)'
        ax.annotate(f"{name}\n{d['correct']}/{d['total']} correct · median {d['median']:.2f}s · p95 {d['p95']:.2f}s",
                    (d['median'], acc), xytext=(0, 18), textcoords='offset points', ha='left', fontsize=10,
                    color=COLORS[tier], fontweight='bold')
    r = lq['router_decision_ms']
    ax.text(0.98, 0.06, f"prompted router decision overhead: {r['median']:.0f} ms median, {r['p95']:.0f} ms p95 "
            f"(n={r['n']})", transform=ax.transAxes, ha='right', fontsize=9.5, color=COLORS['muted'])
    ax.set_xlim(0, 12), ax.set_ylim(55, 90)
    ax.set_xlabel('seconds per prompt (Ollama on M3 MacBook, concurrency 1)')
    ax.set_ylabel('validation correct completions (%)')
    ax.grid(True, color=COLORS['grid']), ax.set_axisbelow(True)
    _save(fig, '07-latency-vs-quality', out, png_dir, written)


def fig_freeze(plt, out, png_dir, written, root):
    fz = freeze_gate(root)
    fig = plt.figure(figsize=(14, 6.4))
    ax = fig.add_axes([0.16, 0.16, 0.48, 0.6])
    _header(fig, 'Held-out test gate: still closed, on purpose',
            'The 500-prompt test split opens only after every tier has complete train/validation coverage '
            'and the configuration is frozen.', SOURCES['freeze'])
    for i, r in enumerate(fz['rows']):
        frac = r['scored'] / r['required']
        ax.barh(i, 1, color=COLORS['missing'], height=0.66)
        if frac:
            ax.barh(i, frac, color=COLORS[r['tier']], height=0.66)
        ax.text(1.02, i, f"{r['scored']:,}/{r['required']:,}", va='center', fontsize=10, color=COLORS['ink'])
    ax.set_yticks(range(len(fz['rows'])), [f"{r['split']} · {r['tier']}" for r in fz['rows']], fontsize=10.5)
    ax.invert_yaxis(), ax.set_xlim(0, 1.2)
    ax.set_xticks([0, 0.5, 1], ['0%', '50%', '100%'])
    ax.set_title('binary-scored observations / required', fontsize=11, pad=8)
    ax.spines['left'].set_visible(False), ax.tick_params(axis='y', length=0)
    fig.text(0.70, 0.76, f"Missing freeze fields ({len(fz['missing_fields'])})", fontsize=11.5,
             fontweight='bold', color=COLORS['ink'], va='top')
    for i, f in enumerate(fz['missing_fields']):
        fig.text(0.70, 0.70 - i * 0.047, f"✗  {f}", fontsize=10, color=COLORS['locked'], va='top')
    fig.text(0.16, 0.06, f"identity issues: {fz['identity_issues']}    ready_for_test: {str(fz['ready']).lower()}    "
             f"test split: {fz['manifest_counts'].get('test', 0)} prompts, unread", fontsize=10, color=COLORS['ink'])
    _save(fig, '08-freeze-gate', out, png_dir, written)


def fig_progress(plt, out, png_dir, written, root):
    commits = commits_per_day(root)
    tests = test_history(root)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={'width_ratios': [1.25, 1]})
    fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.2, wspace=0.18)
    total = sum(n for _, n in commits)
    _header(fig, 'Engineering progress',
            f'{total} local commits across {len(commits)} work days (America/Toronto, counted when generated); '
            f'full offline suite grew from {tests[0][1]} to {tests[-1][1]} passing tests.',
            'git log; full-suite pytest outputs listed in scripts/make_progress_figures.py')
    if commits:
        days = [d[5:] for d, _ in commits]
        vals = [n for _, n in commits]
        bars = a1.bar(days, vals, color=COLORS['small'], width=0.7)
        bars[-1].set_color(COLORS['medium'])
        for b, v in zip(bars, vals):
            a1.text(b.get_x() + b.get_width() / 2, v + 0.4, str(v), ha='center', fontsize=9, color=COLORS['ink'])
        a1.axhline(18, color=COLORS['muted'], ls='--', lw=1)
        a1.text(len(days) - 0.5, 18.4, 'daily target: 18', ha='right', fontsize=9, color=COLORS['muted'])
        a1.set_title('Commits per work day', fontsize=12)
        a1.tick_params(axis='x', rotation=45, labelsize=9)
        a1.yaxis.grid(True, color=COLORS['grid']), a1.set_axisbelow(True)
    else:
        a1.text(0.5, 0.5, 'git history unavailable', ha='center', transform=a1.transAxes)
    days = [d[5:] for d, _ in tests]
    vals = [n for _, n in tests]
    a2.plot(days, vals, color=COLORS['medium'], lw=2.6, marker='o', ms=7, mfc='white', mew=2)
    for d, v in zip(days, vals):
        a2.text(d, v + 5, str(v), ha='center', fontsize=9, color=COLORS['ink'])
    a2.set_ylim(0, max(vals) * 1.15)
    a2.set_title('Passing tests in the full offline suite', fontsize=12)
    a2.tick_params(axis='x', rotation=45, labelsize=9)
    a2.yaxis.grid(True, color=COLORS['grid']), a2.set_axisbelow(True)
    _save(fig, '09-engineering-progress', out, png_dir, written)


FIGURES = [fig_system_map, fig_eval_pipeline, fig_tier_outcomes, fig_transitions, fig_bootstrap,
           fig_policies, fig_latency, fig_freeze, fig_progress]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='SVG output directory')
    parser.add_argument('--png-dir', type=Path, help='also write 200-dpi PNGs here (not committed)')
    args = parser.parse_args(argv)
    plt = _setup()
    written: list[Path] = []
    for fn in FIGURES:
        fn(plt, args.out, args.png_dir, written, ROOT)
    for p in written:
        print(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
