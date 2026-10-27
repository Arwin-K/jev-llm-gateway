import httpx
from fastapi.testclient import TestClient
from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport


def test_explicit_tier_dispatch():
    seen = []

    def handler(request):
        seen.append(request.content.decode())
        return httpx.Response(200, json={"id": "chatcmpl-test", "object": "chat.completion", "choices": [{"message": {"role": "assistant", "content": "hi"}, "finish_reason": "stop", "index": 0}]})

    transport = BackendTransport(2, httpx.MockTransport(handler))
    with TestClient(create_app(from_env(), transport)) as client:
        response = client.post("/v1/chat/completions", json={"model": "medium", "messages": [{"role": "user", "content": "hello"}]})
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hi"
    assert response.headers["x-jev-tier"] == "medium"
    assert '"model":"qwen2.5:7b"' in seen[0]
