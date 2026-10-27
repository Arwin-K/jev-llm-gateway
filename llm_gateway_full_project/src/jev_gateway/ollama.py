"""Native Ollama discovery for Mac self-hosted tiers."""

import httpx

from .config import Backend


async def model_status(client: httpx.AsyncClient, backend: Backend):
    root = backend.base_url.rstrip("/").removesuffix("/v1")
    response = await client.get(root + "/api/tags")
    response.raise_for_status()
    names = {item.get("name") for item in response.json().get("models", [])}
    return {"model": backend.model, "installed": backend.model in names, "runtime": "native-ollama-mac"}


async def loaded_models(client: httpx.AsyncClient, backend: Backend):
    root = backend.base_url.rstrip("/").removesuffix("/v1")
    response = await client.get(root + "/api/ps")
    response.raise_for_status()
    return [{"name": model.get("name"), "size_vram": model.get("size_vram"),
             "expires_at": model.get("expires_at")}
            for model in response.json().get("models", [])]
