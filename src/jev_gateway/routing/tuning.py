"""Validation-only threshold selection from observed decisions and tier outcomes."""
from dataclasses import dataclass
from .contracts import TIERS


@dataclass(frozen=True)
class ValidationCase:
    prompt_id: str
    split: str
    probabilities: dict[str, float]
    outcomes: dict[str, str]
    charges_usd: dict[str, float | None]
    decision_charge_usd: float | None = None


def evaluate(cases: list[ValidationCase], thresholds: dict[str, float]) -> dict:
    if not cases or any(case.split != 'validation' for case in cases):
        raise PermissionError('operating points use nonempty validation data only')
    if set(thresholds) != set(TIERS) or any(not 0 <= x <= 1 for x in thresholds.values()):
        raise ValueError('thresholds required for every tier')
    expected = len(cases)
    scored = correct = abstained = missing = 0
    cost = 0.
    cost_known = True
    for case in cases:
        tier = next((t for t in TIERS if case.probabilities.get(t, -1) >= thresholds[t]), None)
        if tier is None:
            abstained += 1
            continue
        outcome = case.outcomes.get(tier)
        if outcome not in {'correct','incorrect','parse_error'}:
            missing += 1
            continue
        scored += 1
        correct += outcome == 'correct'
        charge = case.charges_usd.get(tier)
        if charge is None or case.decision_charge_usd is None:
            cost_known = False
        else:
            cost += charge + case.decision_charge_usd
    return {'thresholds':thresholds, 'expected':expected, 'scored':scored,
            'correct':correct, 'abstained':abstained, 'missing':missing,
            'coverage':scored/expected, 'correct_completion_rate':correct/expected,
            'scored_accuracy':correct/scored if scored else None,
            'total_charge_usd':cost if cost_known else None,
            'execution':'offline_replay'}


def select(cases: list[ValidationCase], candidates: list[dict[str, float]], *,
           min_correct_completion_rate: float, min_coverage: float = 1.) -> dict:
    if not cases or any(case.split != 'validation' for case in cases):
        raise PermissionError('operating points use nonempty validation data only')
    if not 0 <= min_correct_completion_rate <= 1 or not 0 <= min_coverage <= 1:
        raise ValueError('objectives must be probabilities')
    reports = [evaluate(cases, candidate) for candidate in candidates]
    feasible = [r for r in reports if r['coverage'] >= min_coverage and
                r['correct_completion_rate'] >= min_correct_completion_rate and
                r['total_charge_usd'] is not None]
    winner = min(feasible, key=lambda r:(r['total_charge_usd'], -r['correct_completion_rate'])) if feasible else None
    return {'objective':{'min_correct_completion_rate':min_correct_completion_rate,
                         'min_coverage':min_coverage, 'minimize':'total observed charge_usd'},
            'candidates':reports, 'selected':winner,
            'selection_reason':'lowest observed charge among feasible validation candidates' if winner else
                               'no candidate meets coverage, quality, and known-cost requirements'}


def main(argv=None):
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--min-quality', type=float, required=True)
    parser.add_argument('--min-coverage', type=float, default=1.)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.output.resolve().is_relative_to(Path('runs').resolve()):
        parser.error('selection evidence must be stored under runs/')
    cases = [ValidationCase(**json.loads(line)) for line in args.cases.read_text().splitlines() if line]
    report = select(cases, json.loads(args.candidates.read_text()),
                    min_correct_completion_rate=args.min_quality, min_coverage=args.min_coverage)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps({'output':str(args.output), 'selected':report['selected'] is not None}))


if __name__ == '__main__':
    main()
