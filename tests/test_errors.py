import httpx
from fastapi.testclient import TestClient
from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport


def call(handler, stream=False):
    transport = BackendTransport(2, httpx.MockTransport(handler))
    with TestClient(create_app(from_env(), transport)) as client:
        return client.post("/v1/chat/completions", json={"model": "small", "messages": [{"role": "user", "content": "hi"}], "stream": stream})


def test_backend_error_is_sanitized_even_for_stream():
    for streaming in (False, True):
        response = call(lambda request: httpx.Response(500, text="secret provider detail"), streaming)
        assert response.status_code == 502
        assert "secret provider detail" not in response.text


def test_timeout_is_gateway_timeout():
    def handler(request):
        raise httpx.ReadTimeout("timeout")
    assert call(handler).status_code == 504
