import pytest

from jev_gateway.day6.uncertainty import paired_difference


def test_pairing_retains_group_units():
    left = {'a': 0, 'b': 0, 'c': 1}
    right = {'a': 1, 'b': 1, 'c': 1}
    groups = {'a': 'first', 'b': 'first', 'c': 'second'}
    result = paired_difference(left, right, groups=groups, repetitions=200)
    assert result['group_count'] == 2
    assert result['mean_right_minus_left'] == pytest.approx(2/3)
    assert result == paired_difference(left, right, groups=groups, repetitions=200)
