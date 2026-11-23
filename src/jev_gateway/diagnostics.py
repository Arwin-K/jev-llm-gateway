"""Real, bounded diagnostics. No implicit test doubles."""

import asyncio
import json

import httpx

from .config import ConfigError, from_env
from .ollama import loaded_models, model_status


async def _decision_status(settings, client):
    policy = settings.router_policy
    required = policy in {"laya-choice", "laya-threshold", "jev-choice", "jev-threshold"}
    status = {
        "provider": settings.decision_provider,
        "model": settings.jev_model,
        "policy": policy,
        "required": required,
        "enabled": settings.decision_enabled,
    }
    if not required:
        status.update(available=None, reason="router_policy_does_not_require_decision_service")
        return status
    if not settings.decision_enabled:
        status.update(available=False, reason="decision_backend_disabled_or_missing_positive_caps")
        return status
    if settings.decision_provider != "laya":
        # Do not make an external request from doctor: this can be a paid provider.
        status.update(available=None, reason="hosted_provider_not_probed")
        return status
    try:
        response = await client.get(settings.decision_url.rstrip("/") + "/health")
        response.raise_for_status()
        status.update(available=True, health_status=response.status_code)
    except (httpx.HTTPError, ValueError) as exc:
        status.update(available=False, reason=type(exc).__name__)
    return status


async def _doctor():
    settings = from_env()
    report = {"frontier": {"configured": settings.frontier_enabled}, "tiers": {}}
    async with httpx.AsyncClient(timeout=3) as client:
        report["decision"] = await _decision_status(settings, client)
        for tier in ("small", "medium"):
            backend = settings.backend(tier)
            try:
                status = await model_status(client, backend)
                status["loaded_models"] = await loaded_models(client, backend)
            except (httpx.HTTPError, ValueError) as exc:
                status = {"model": backend.model, "available": False, "reason": type(exc).__name__}
            report["tiers"][tier] = status
    return report


def doctor():
    try:
        report = asyncio.run(_doctor())
    except ConfigError as exc:
        print(f"configuration error: {exc}")
        return 2
    print(json.dumps(report, indent=2))
    tiers_ready = all(item.get("installed") for item in report["tiers"].values())
    decision = report.get("decision", {})
    decision_ready = not decision.get("required", False) or decision.get("available") is not False
    return 0 if tiers_ready and decision_ready else 1


def smoke(tier="small", gateway_url="http://127.0.0.1:8080"):
    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(gateway_url.rstrip("/") + "/v1/chat/completions", json={
                "model": tier, "messages": [{"role": "user", "content": "Reply with one short greeting."}],
                "max_tokens": 16,
            })
            response.raise_for_status()
            data = response.json()
            print(json.dumps({"tier": tier, "request_id": response.headers.get("x-request-id"),
                              "backend_model": response.headers.get("x-jev-backend-model"),
                              "answer": data["choices"][0]["message"]["content"]}))
            return 0
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        print(f"smoke failed: {type(exc).__name__}: {exc}")
        return 1
