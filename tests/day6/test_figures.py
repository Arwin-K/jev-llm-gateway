import json

from jev_gateway.day6.figures import coverage_svg


def test_figure_contains_coverage_denominator_and_hash(tmp_path):
    path = tmp_path / 'audit.json'
    path.write_text(json.dumps({'schema': 'jev.day6.freeze_audit.v1',
                                'scored_observations': {'validation/small': 0},
                                'required_scored_observations': {'validation/small': 500}}))
    svg = coverage_svg(path)
    assert '0/500 scored' in svg
    assert 'Input SHA-256:' in svg
