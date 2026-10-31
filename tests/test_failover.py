import httpx
from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport
from jev_gateway.routing.contracts import Decision


class SmallRouter:
    async def decide(self, request):
        return Decision("small", "fixed", "1", .1, request_id=request.request_id)


def test_local_failover_keeps_frontier_out_and_records_origin(monkeypatch, caplog):
    caplog.set_level("INFO", logger="jev_gateway.trace")
    monkeypatch.setenv("JEV_AVAILABILITY_FAILOVER_ENABLED", "true")
    calls = []
    def backend(request):
        model = request.read().decode()
        calls.append(model)
        if 'qwen2.5:1.5b' in model:
            return httpx.Response(503, json={"error": "unavailable"})
        return httpx.Response(200, json={"id": "ok", "choices": [{"message": {"content": "hello"}}]})
    transport = BackendTransport(2, httpx.MockTransport(backend))
    with TestClient(create_app(from_env(), transport, router=SmallRouter())) as client:
        result = client.post("/v1/chat/completions", json={"model": "auto", "messages": [
            {"role": "user", "content": "hello"}]})
    assert result.status_code == 200
    assert result.headers["x-jev-tier"] == "medium"
    assert len(calls) == 2
    assert '"original_tier":"small"' in caplog.text


def test_nonretryable_backend_failure_does_not_failover(monkeypatch):
    monkeypatch.setenv("JEV_AVAILABILITY_FAILOVER_ENABLED", "true")
    calls = []
    def backend(request):
        calls.append(1)
        return httpx.Response(400)
    with TestClient(create_app(from_env(), BackendTransport(2, httpx.MockTransport(backend)),
                               router=SmallRouter())) as client:
        result = client.post("/v1/chat/completions", json={"model": "auto", "messages": [
            {"role": "user", "content": "hello"}]})
    assert result.status_code == 502 and len(calls) == 1
