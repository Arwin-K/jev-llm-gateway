import asyncio
import httpx
from jev_gateway.config import Backend
from jev_gateway.transport import BackendTransport


def test_forwarding_and_close():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = request.read().decode()
        return httpx.Response(200, json={"choices": []})

    async def run():
        transport = BackendTransport(2, httpx.MockTransport(handler))
        result = await transport.complete(Backend("small", "x", "http://localhost:11434/v1"), {"model": "x"})
        await transport.close()
        assert result == {"choices": []}

    asyncio.run(run())
    assert seen["path"] == "/v1/chat/completions"
    assert '"model":"x"' in seen["body"]
