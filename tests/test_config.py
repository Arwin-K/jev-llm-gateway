import pytest
from laya_gateway.config import Backend, ConfigError, from_env


def test_invalid_backend_url():
    with pytest.raises(ConfigError, match="absolute HTTP"):
        Backend("small", "x", "file:///tmp/model")


def test_frontier_requires_positive_caps_and_key(monkeypatch):
    monkeypatch.setenv("LAYA_GATEWAY_FRONTIER_MODEL", "example")
    monkeypatch.setenv("LAYA_GATEWAY_FRONTIER_API_KEY", "secret")
    assert not from_env().frontier_enabled


def test_invalid_limit(monkeypatch):
    monkeypatch.setenv("LAYA_GATEWAY_MAX_OUTPUT_TOKENS", "zero")
    with pytest.raises(ConfigError, match="integer"):
        from_env()
