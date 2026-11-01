import json

import pytest

from jev_gateway.day6.cost_report import reconcile


def test_unknown_rejected_attempt_keeps_total_unknown(tmp_path):
    path = tmp_path / 'ledger.json'
    path.write_text(json.dumps({'stages': [
        {'stage': 'generation', 'status': 'known_charge', 'charge_usd': 0.02},
        {'stage': 'rejected_attempt', 'status': 'unknown', 'charge_usd': None}]}))
    report = reconcile(path, capacity_hourly_usd=3, allocated_hours=2, busy_hours=.5)
    assert report['recorded_charge_usd'] == .02
    assert report['total_charge_usd'] is None
    assert report['capacity_scenario']['modeled_charge_usd'] == 6
    with pytest.raises(ValueError, match='complete'):
        reconcile(path, allocated_hours=2)
