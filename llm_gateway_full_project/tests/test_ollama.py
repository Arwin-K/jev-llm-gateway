import asyncio
import httpx
from jev_gateway.config import Backend
from jev_gateway.ollama import loaded_models, model_status


def test_native_model_identity():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"models": [{"name": "qwen2.5:1.5b"}]}))) as client:
            return await model_status(client, Backend("small", "qwen2.5:1.5b", "http://localhost:11434/v1"))
    assert asyncio.run(run())["installed"] is True


def test_loaded_model_observation():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"models": [{"name": "qwen2.5:7b", "size_vram": 4000}]}))) as client:
            return await loaded_models(client, Backend("medium", "qwen2.5:7b", "http://localhost:11434/v1"))
    assert asyncio.run(run())[0]["size_vram"] == 4000
