from dataclasses import replace

from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.config import from_env


def test_required_trained_fallback_prevents_false_readiness():
    settings = replace(from_env(), router_policy="always-small", require_trained_fallback=True)
    with TestClient(create_app(settings)) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 503


def test_process_readiness_does_not_claim_backend_residency():
    settings = replace(from_env(), router_policy="always-small")
    with TestClient(create_app(settings)) as client:
        result = client.get("/readyz")
    assert result.status_code == 200
    assert result.json()["backend_availability"] == "unchecked"
