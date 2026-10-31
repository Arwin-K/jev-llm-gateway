from dataclasses import replace

import httpx
from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.routing.contracts import Decision
from jev_gateway.routing.jev_choice import JevChoiceRouter
from jev_gateway.routing.jev_client import JevClient
from jev_gateway.transport import BackendTransport


class FixtureTrainedFallback:
    name = "distilbert"
    version = "fixture"

    async def decide(self, request):
        return Decision("small", self.name, self.version, .1,
                        request_id=request.request_id,
                        settings_fingerprint=request.settings_fingerprint)


def test_controlled_jev_outage_breaker_fallback_and_recovery(monkeypatch, caplog):
    caplog.set_level("INFO", logger="jev_gateway.trace")
    monkeypatch.setenv("TYPESAFE_API_KEY", "offline-fixture-only")
    settings = replace(from_env(), jev_model="fixture", jev_max_requests=10,
                       jev_max_tokens=100000, jev_max_usd=1,
                       jev_input_usd_per_million=1, jev_output_usd_per_million=1,
                       jev_rate_source_url="https://example.invalid/fixture",
                       jev_rate_effective_date="2026-10-31", jev_breaker_failures=2,
                       jev_breaker_cooldown_seconds=30)
    calls = []
    def jev(request):
        calls.append(request)
        if len(calls) <= 2:
            return httpx.Response(503)
        return httpx.Response(200, json={"model": "fixture", "answers": {"route": {
            "type": "choice", "choice": "small", "probabilities": {"small": 1., "medium": 0.}}}})
    jev_client = JevClient(settings, httpx.MockTransport(jev))
    now = [0.]
    jev_client.breaker.clock = lambda: now[0]
    router = JevChoiceRouter(settings, jev_client)
    transport = BackendTransport(2, httpx.MockTransport(lambda _: httpx.Response(200, json={
        "id": "fixture", "choices": [{"message": {"content": "four"}}]})))
    with TestClient(create_app(settings, transport, router=router,
                               fallback_router=FixtureTrainedFallback())) as client:
        responses = [client.post("/v1/chat/completions", json={"model": "auto", "messages": [
            {"role": "user", "content": "two plus two"}]}) for _ in range(3)]
        assert all(response.status_code == 200 for response in responses)
        assert len(calls) == 2 and jev_client.breaker.state == "open"
        now[0] = 31
        recovered = client.post("/v1/chat/completions", json={"model": "auto", "messages": [
            {"role": "user", "content": "two plus two"}]})
        assert recovered.status_code == 200
        assert jev_client.breaker.state == "closed"
        metrics = client.get("/metrics").text
    assert 'jev_routing_decisions_total{outcome="fallback_selected",fallback="yes"} 3.0' in metrics
    assert 'jev_breaker_transitions_total{state="open"} 1.0' in metrics
    assert 'jev_breaker_transitions_total{state="half_open"} 1.0' in metrics
    assert 'jev_breaker_transitions_total{state="closed"} 1.0' in metrics
    assert 'jev_client_requests_total{mode="standard",status="200"} 4.0' in metrics
    assert '"outcome":"fallback_selected"' in caplog.text


def test_verifier_outage_does_not_use_tier_classifier_as_answer_verifier(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "offline-fixture-only")
    settings = replace(from_env(), jev_model="fixture", jev_max_requests=10,
                       jev_max_tokens=100000, jev_max_usd=1,
                       jev_input_usd_per_million=1, jev_output_usd_per_million=1,
                       jev_rate_source_url="https://example.invalid/fixture",
                       jev_rate_effective_date="2026-10-31", execution_paid_enabled=True,
                       execution_max_requests=10, execution_max_tokens=100000,
                       execution_max_usd=1, verification_threshold=.8,
                       verification_threshold_source="offline-fixture")
    class OutageVerifier:
        async def judge(self, request, *, deadline_seconds=None):
            raise RuntimeError("controlled Jev outage")
    transport = BackendTransport(2, httpx.MockTransport(lambda _: httpx.Response(200, json={
        "id": "fixture", "choices": [{"message": {"content": "four"}}]})))
    with TestClient(create_app(settings, transport, router=FixtureTrainedFallback(),
                               answer_verifier=OutageVerifier())) as client:
        result = client.post("/v1/chat/completions", json={"model": "small",
            "execution_mode": "cascade", "messages": [{"role": "user", "content": "two plus two"}]})
        metrics = client.get("/metrics").text
    assert result.status_code == 503
    assert 'jev_verification_outcomes_total{outcome="verification_failed"} 1.0' in metrics
