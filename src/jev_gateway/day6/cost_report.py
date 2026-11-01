"""Reconcile every stage without treating missing cost as zero."""

import argparse
from collections import Counter
from pathlib import Path

from .common import digest, read_json, write_new

STAGES = ('generation', 'routing', 'verification', 'embedding', 'candidate_check', 'retry', 'rejected_attempt')


def reconcile(path: Path, *, capacity_hourly_usd: float | None = None,
              allocated_hours: float | None = None, busy_hours: float | None = None) -> dict:
    rows = read_json(path).get('stages')
    if not isinstance(rows, list):
        raise ValueError('stages must be a list')
    counts = Counter()
    known = 0.0
    estimated = 0.0
    unknown = []
    for index, row in enumerate(rows):
        stage, status, amount = row.get('stage'), row.get('status'), row.get('charge_usd')
        if stage not in STAGES or status not in ('known_charge', 'estimated_api', 'unknown'):
            raise ValueError(f'invalid stage or status at row {index}')
        if status == 'unknown':
            if amount is not None:
                raise ValueError('unknown cost must be null')
            unknown.append(index)
        else:
            if not isinstance(amount, (int, float)) or amount < 0:
                raise ValueError('known or estimated cost must be nonnegative')
            if status == 'estimated_api' and not (row.get('rate_source_url', '').startswith('https://')
                                                  and row.get('rate_effective_date')):
                raise ValueError('estimated API charges require dated source')
            if status == 'known_charge':
                known += amount
            else:
                estimated += amount
        counts[stage] += 1
    capacity = None
    if any(v is not None for v in (capacity_hourly_usd, allocated_hours, busy_hours)):
        if any(v is None or v < 0 for v in (capacity_hourly_usd, allocated_hours, busy_hours)) or busy_hours > allocated_hours:
            raise ValueError('complete nonnegative capacity scenario required')
        capacity = {'status': 'modeled_capacity', 'allocated_hours': allocated_hours,
                    'busy_hours': busy_hours, 'idle_hours': allocated_hours-busy_hours,
                    'hourly_usd': capacity_hourly_usd,
                    'modeled_charge_usd': capacity_hourly_usd*allocated_hours}
    return {'schema': 'jev.day6.cost_report.v1', 'input_sha256': digest(path),
            'stage_counts': {stage: counts[stage] for stage in STAGES},
            'recorded_charge_usd': known, 'estimated_api_charge_usd': estimated,
            'unknown_stage_indices': unknown, 'total_charge_usd': None if unknown else known+estimated,
            'capacity_scenario': capacity}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--capacity-hourly-usd', type=float)
    parser.add_argument('--allocated-hours', type=float)
    parser.add_argument('--busy-hours', type=float)
    args = parser.parse_args(argv)
    write_new(args.output, reconcile(args.input, capacity_hourly_usd=args.capacity_hourly_usd,
                                     allocated_hours=args.allocated_hours, busy_hours=args.busy_hours))


if __name__ == '__main__':
    main()
