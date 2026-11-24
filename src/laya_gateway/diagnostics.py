"""Native model diagnostics and one-request CLI smoke check."""
import asyncio
import json

import httpx

from .chat import complete_local
from .config import ConfigError, from_env
from .ollama import loaded_models, model_status
from .routing.laya_runtime import LayaRuntime


async def _doctor():
    settings = from_env()
    import torch
    accelerator_available = None
    if settings.laya_device == "mps":
        accelerator_available = torch.backends.mps.is_available()
    elif settings.laya_device.startswith("cuda"):
        accelerator_available = torch.cuda.is_available()
    requested_device = settings.laya_device
    actual_device = ("cpu" if accelerator_available is False else requested_device)
    report = {"decision": {"provider": "native-laya", "model": settings.laya_model,
                           "device_requested": requested_device, "device_used": actual_device,
                           "accelerator_available": accelerator_available, "available": False}, "tiers": {}}
    async with httpx.AsyncClient(timeout=3) as client:
        for tier in ("small", "medium"):
            backend = settings.backend(tier)
            try:
                status = await model_status(client, backend)
                status["loaded_models"] = await loaded_models(client, backend)
            except (httpx.HTTPError, ValueError) as exc:
                status = {"model": backend.model, "installed": False, "reason": type(exc).__name__}
            report["tiers"][tier] = status
    runtime = LayaRuntime(settings)
    try:
        await runtime.initialize()
        report["decision"].update(available=True, loaded=True)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        report["decision"].update(available=False, reason=type(exc).__name__)
    finally:
        runtime.close()
    return report


def doctor():
    try:
        report = asyncio.run(_doctor())
    except ConfigError as exc:
        print(f"configuration error: {exc}")
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["decision"]["available"] and all(
        item.get("installed") for item in report["tiers"].values()) else 1


def smoke(tier="auto"):
    try:
        result = asyncio.run(complete_local(from_env(), "Reply with one short greeting.", tier=tier,
                                            max_tokens=16))
        print(json.dumps({"tier": result.tier, "backend_model": result.model,
                          "decision_ms": result.decision_ms, "answer": result.answer}))
        return 0
    except (httpx.HTTPError, KeyError, ValueError, RuntimeError) as exc:
        print(f"smoke failed: {type(exc).__name__}: {exc}")
        return 1
