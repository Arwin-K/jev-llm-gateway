import httpx
from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport


def test_client_metrics_count_once_and_never_label_request_content():
    secret = "private-user-prompt"
    response_body = {"id": "test", "object": "chat.completion", "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 1}}
    transport = BackendTransport(2, httpx.MockTransport(lambda _: httpx.Response(200, json=response_body)))
    with TestClient(create_app(from_env(), transport)) as client:
        result = client.post("/v1/chat/completions", json={"model": "small", "messages": [
            {"role": "user", "content": secret}]})
        assert result.status_code == 200
        invalid = client.post("/v1/chat/completions", json={"model": "invalid", "messages": []})
        assert invalid.status_code == 422
        metrics = client.get("/metrics").text
    assert 'jev_client_requests_total{mode="standard",status="200"} 1.0' in metrics
    assert 'jev_client_requests_total{mode="standard",status="422"} 1.0' in metrics
    assert 'jev_selected_tier_total{tier="small"} 1.0' in metrics
    assert 'jev_known_tokens_total{kind="prompt_tokens"} 3.0' in metrics
    assert secret not in metrics
    assert 'jev_active_requests 0' in metrics
