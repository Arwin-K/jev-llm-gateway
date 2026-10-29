import pytest
from jev_gateway.config import Backend, ConfigError, from_env


def test_invalid_backend_url():
    with pytest.raises(ConfigError, match="absolute HTTP"):
        Backend("small", "x", "file:///tmp/model")


def test_frontier_requires_positive_caps_and_key(monkeypatch):
    monkeypatch.setenv("JEV_FRONTIER_MODEL", "example")
    monkeypatch.setenv("JEV_FRONTIER_API_KEY", "secret")
    assert not from_env().frontier_enabled


def test_invalid_limit(monkeypatch):
    monkeypatch.setenv("JEV_MAX_OUTPUT_TOKENS", "zero")
    with pytest.raises(ConfigError, match="integer"):
        from_env()
