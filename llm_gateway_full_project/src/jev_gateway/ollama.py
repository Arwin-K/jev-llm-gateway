"""Native Ollama discovery for Mac self-hosted tiers."""

import httpx

from .config import Backend


async def model_status(client: httpx.AsyncClient, backend: Backend):
    root = backend.base_url.rstrip("/").removesuffix("/v1")
    response = await client.get(root + "/api/tags")
    response.raise_for_status()
    names = {item.get("name") for item in response.json().get("models", [])}
    return {"model": backend.model, "installed": backend.model in names, "runtime": "native-ollama-mac"}
