import asyncio

import httpx

from jev_gateway import diagnostics
from jev_gateway.diagnostics import smoke
from jev_gateway.config import from_env


def test_smoke_reports_unavailable_gateway(capsys):
    assert smoke(gateway_url="http://127.0.0.1:1") == 1
    assert "smoke failed" in capsys.readouterr().out


def laya_settings(monkeypatch):
    monkeypatch.setenv("JEV_DECISION_MAX_REQUESTS", "1")
    monkeypatch.setenv("JEV_DECISION_MAX_TOKENS", "1000")
    return from_env()


def test_decision_doctor_checks_local_laya_health(monkeypatch):
    settings = laya_settings(monkeypatch)
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"status": "ok"})

    async def check():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await diagnostics._decision_status(settings, client)

    report = asyncio.run(check())
    assert report["required"] and report["enabled"] and report["available"]
    assert seen[0].url == "http://127.0.0.1:8000/health"


def test_decision_doctor_reports_disabled_laya_without_network(monkeypatch):
    monkeypatch.delenv("JEV_DECISION_MAX_REQUESTS", raising=False)
    monkeypatch.delenv("JEV_DECISION_MAX_TOKENS", raising=False)
    settings = from_env()

    async def check():
        async with httpx.AsyncClient(transport=httpx.MockTransport(
                lambda request: (_ for _ in ()).throw(AssertionError("unexpected network")))) as client:
            return await diagnostics._decision_status(settings, client)

    report = asyncio.run(check())
    assert report["available"] is False
    assert report["reason"] == "decision_backend_disabled_or_missing_positive_caps"


def test_doctor_fails_when_required_laya_is_unavailable(monkeypatch, capsys):
    async def report():
        return {
            "decision": {"required": True, "available": False},
            "tiers": {"small": {"installed": True}, "medium": {"installed": True}},
            "frontier": {"configured": False},
        }

    monkeypatch.setattr(diagnostics, "_doctor", report)
    assert diagnostics.doctor() == 1
    assert '"available": false' in capsys.readouterr().out
