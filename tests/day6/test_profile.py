import pytest

from jev_gateway.day6.profile import collect


def test_missing_profiler_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setattr('jev_gateway.day6.profile.shutil.which', lambda name: None)
    with pytest.raises(RuntimeError, match='no profile artifact'):
        collect(tmp_path, ['python', '-c', 'pass'], 5)
