import json
import httpx
from fastapi.testclient import TestClient
from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport


def test_mac_and_colab_profile_dispatch(monkeypatch):
    for url in ("http://127.0.0.1:11434/v1", "http://127.0.0.1:8000/v1"):
        monkeypatch.setenv("JEV_SMALL_URL", url)
        seen = []

        def handler(request):
            seen.append((str(request.url), json.loads(request.content)))
            return httpx.Response(200, json={"id": "fixture", "object": "chat.completion", "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})

        transport = BackendTransport(2, httpx.MockTransport(handler))
        with TestClient(create_app(from_env(), transport)) as client:
            response = client.post("/v1/chat/completions", json={"model": "small", "messages": [{"role": "user", "content": "hi"}]})
        assert response.status_code == 200
        assert seen[0][0].startswith(url)
        assert seen[0][1]["model"] == "qwen2.5:1.5b"
        assert response.headers["x-request-id"]
