"""Bounded reusable HTTP transport for OpenAI-compatible chat servers."""

from contextlib import asynccontextmanager

import httpx

from .config import Backend


class BackendTransport:
    def __init__(self, timeout: float, transport: httpx.AsyncBaseTransport | None = None):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            transport=transport,
        )

    async def close(self):
        await self.client.aclose()

    def _request(self, backend: Backend, payload: dict):
        headers = {"content-type": "application/json"}
        if backend.api_key:
            headers["authorization"] = f"Bearer {backend.api_key}"
        return self.client.build_request("POST", backend.base_url.rstrip("/") + "/chat/completions", json=payload, headers=headers)

    async def complete(self, backend: Backend, payload: dict):
        response = await self.client.send(self._request(backend, payload))
        response.raise_for_status()
        return response.json()

    @asynccontextmanager
    async def stream(self, backend: Backend, payload: dict):
        response = await self.client.send(self._request(backend, payload), stream=True)
        try:
            response.raise_for_status()
            yield response
        finally:
            await response.aclose()

    async def open_stream(self, backend: Backend, payload: dict):
        response = await self.client.send(self._request(backend, payload), stream=True)
        try:
            response.raise_for_status()
            return response
        except BaseException:
            await response.aclose()
            raise
