import httpx
from fastapi.testclient import TestClient
from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.transport import BackendTransport


class Fragments(httpx.AsyncByteStream):
    async def __aiter__(self):
        yield b'data: {"choices":[{"delta":{"content":"he"}}]}\n\n'
        yield b'data: {"choices":[{"delta":{"content":"llo"}}]}\n\n'
        yield b'data: [DONE]\n\n'


def test_sse_fragments_and_completion():
    transport = BackendTransport(2, httpx.MockTransport(lambda request: httpx.Response(
        200, headers={"content-type": "text/event-stream"}, stream=Fragments())))
    with TestClient(create_app(from_env(), transport)) as client:
        with client.stream("POST", "/v1/chat/completions", json={"model": "small", "messages": [{"role": "user", "content": "hi"}], "stream": True}) as response:
            body = b"".join(response.iter_raw())
            assert response.headers["x-jev-tier"] == "small"
    assert b'"he"' in body and b'"llo"' in body and body.endswith(b"data: [DONE]\n\n")
