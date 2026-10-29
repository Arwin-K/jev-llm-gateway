"""Validation offline replay: quality/cost coverage and a bounded SVG frontier."""
import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from jev_gateway.evaluation.manifest import load
from jev_gateway.evaluation.oracle import label as oracle_label
from jev_gateway.evaluation.records import Result
from .contracts import TIERS


@dataclass(frozen=True)
class Selection:
    prompt_id: str
    policy: str
    tier: str
    decision_charge_usd: float | None = None
    decision_duration_ms: float | None = None
    execution: str = 'offline_replay'


def baselines(prompts, *, seed: int = 17) -> list[Selection]:
    out = []
    for prompt in prompts:
        for tier in TIERS:
            out.append(Selection(prompt.prompt_id, f'always-{tier}', tier, 0.))
        index = int.from_bytes(hashlib.sha256(f'{seed}:{prompt.prompt_id}'.encode()).digest()[:8], 'big') % 3
        out.append(Selection(prompt.prompt_id, f'seeded-random-{seed}', TIERS[index], 0.))
    return out


def hindsight(prompts, results) -> list[Selection]:
    grouped = {}
    for result in results:
        grouped.setdefault(result.prompt_id, []).append(result)
    out = []
    for prompt in prompts:
        if prompt.split != 'validation':
            raise PermissionError('validation comparison only')
        oracle = oracle_label(prompt, grouped.get(prompt.prompt_id, []), allowed_split='validation')
        if oracle.status == 'labeled':
            out.append(Selection(prompt.prompt_id, 'observed-hindsight-oracle', oracle.tier, 0.))
    return out


def compare(prompts, results: list[Result], selections: list[Selection], policy_names=()) -> list[dict]:
    if not prompts or any(p.split != 'validation' for p in prompts):
        raise PermissionError('comparison requires nonempty validation prompts')
    expected_ids = {p.prompt_id for p in prompts}
    observed = {(r.prompt_id,r.tier):r for r in results if r.split == 'validation' and r.execution == 'real'}
    policies = sorted({s.policy for s in selections} | set(policy_names))
    reports = []
    for policy in policies:
        choices = [s for s in selections if s.policy == policy and s.prompt_id in expected_ids]
        if len({s.prompt_id for s in choices}) != len(choices):
            raise ValueError('duplicate policy selection for prompt')
        correct = scored = missing = failed = 0
        charges = 0.
        cost_known = True
        overhead_count = 0
        for selection in choices:
            if selection.tier not in TIERS:
                raise ValueError('unsupported tier selection')
            result = observed.get((selection.prompt_id, selection.tier))
            if result is None:
                missing += 1
                continue
            if result.outcome in {'correct','incorrect','parse_error'}:
                scored += 1
                correct += result.outcome == 'correct'
            else:
                failed += 1
            if result.charge_usd is None or selection.decision_charge_usd is None:
                cost_known = False
            else:
                charges += result.charge_usd + selection.decision_charge_usd
            overhead_count += selection.decision_duration_ms is not None
        expected = len(prompts)
        reports.append({'policy':policy, 'expected':expected, 'selected':len(choices),
                        'unselected':expected-len(choices), 'missing_result':missing,
                        'failed_result':failed, 'scored':scored, 'correct':correct,
                        'correct_completion_rate':correct/expected,
                        'scored_accuracy':correct/scored if scored else None,
                        'total_charge_usd':charges if cost_known and len(choices)==expected and not missing else None,
                        'decision_overhead_observed':overhead_count,
                        'execution':'offline_replay'})
    return reports


def write_frontier_svg(reports: list[dict], path: Path):
    points = [r for r in reports if r['total_charge_usd'] is not None and r['scored']]
    max_cost = max((r['total_charge_usd'] for r in points), default=1) or 1
    circles = ''.join(f'<circle cx="{50+330*r["total_charge_usd"]/max_cost:.1f}" '
                      f'cy="{350-300*r["correct_completion_rate"]:.1f}" r="4" fill="#185abc"/>'
                      f'<text x="{55+330*r["total_charge_usd"]/max_cost:.1f}" '
                      f'y="{347-300*r["correct_completion_rate"]:.1f}" font-size="10">'
                      f'{escape(r["policy"])} (n={r["scored"]})</text>' for r in points)
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="400">'
                    '<rect width="500" height="400" fill="white"/>'
                    '<text x="30" y="20" font-size="14">Validation offline replay; observed cost only</text>'
                    '<line x1="50" y1="350" x2="380" y2="350" stroke="black"/>'
                    '<line x1="50" y1="350" x2="50" y2="50" stroke="black"/>'
                    '<text x="140" y="385" font-size="11">Total observed charge (USD)</text>'
                    + circles + '</svg>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('runs/day2-manifest.jsonl'))
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--selections', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--seed', type=int, default=17)
    args = parser.parse_args(argv)
    if args.output is None:
        import uuid
        args.output = Path('runs')/f'day3-validation-comparison-{uuid.uuid4().hex}.json'
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('comparison output must be under runs/')
    prompts = load(args.manifest, 'validation')
    results = [Result.model_validate_json(line) for line in args.run.read_text().splitlines() if line]
    selections = baselines(prompts, seed=args.seed) + hindsight(prompts, results)
    if args.selections:
        selections += [Selection(**json.loads(line)) for line in args.selections.read_text().splitlines() if line]
    reports = compare(prompts, results, selections, policy_names=[
        'always-small','always-medium','always-frontier',f'seeded-random-{args.seed}',
        'observed-hindsight-oracle','distilbert','prompted-small','jev-choice',
        'jev-threshold','strands-decider'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(reports, indent=2))
    write_frontier_svg(reports, args.output.with_suffix('.svg'))
    print(json.dumps({'report':str(args.output), 'figure':str(args.output.with_suffix('.svg')),
                      'policies':len(reports), 'plotted':sum(r['total_charge_usd'] is not None and r['scored']>0 for r in reports)}))


if __name__ == '__main__':
    main()
