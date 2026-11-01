"""Summarize actual validation replay coverage before composed-system claims."""

import argparse
import json
from pathlib import Path

from .common import digest, write_new

ROUTER_POLICIES = ('always-small', 'always-medium', 'always-frontier', 'seeded-random-17',
                   'distilbert', 'prompted-small', 'jev-choice', 'jev-threshold',
                   'strands-decider', 'observed-hindsight-oracle')
CACHE_MODES = ('disabled', 'similarity_only', 'verified')


def audit(router: Path, cache: Path) -> dict:
    routing = json.loads(router.read_text())
    caching = json.loads(cache.read_text())
    if not isinstance(routing, list) or not isinstance(caching, list):
        raise ValueError('expected list reports')
    routes = {row['policy']: row for row in routing}
    modes = {row['mode']: row for row in caching if row['execution'] == 'real'}
    return {'schema': 'jev.day6.system_audit.v1',
            'router_report_sha256': digest(router), 'cache_report_sha256': digest(cache),
            'routing': {name: {'selected': routes.get(name, {}).get('selected', 0),
                               'scored': routes.get(name, {}).get('scored', 0),
                               'missing_result': routes.get(name, {}).get('missing_result')}
                        for name in ROUTER_POLICIES},
            'cache': {name: {'observed': modes.get(name, {}).get('observed', 0),
                             'scored': modes.get(name, {}).get('scored', 0),
                             'comparison_compatible': modes.get(name, {}).get('comparison_compatible', False)}
                      for name in CACHE_MODES},
            'held_out_composed_comparison': 'pending',
            'real_quality_comparison_ready': all(routes.get(name, {}).get('scored', 0) > 0 for name in ROUTER_POLICIES)
                                             and all(modes.get(name, {}).get('comparison_compatible', False)
                                                     for name in CACHE_MODES)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--router-report', type=Path, required=True)
    parser.add_argument('--cache-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    write_new(args.output, audit(args.router_report, args.cache_report))


if __name__ == '__main__':
    main()
