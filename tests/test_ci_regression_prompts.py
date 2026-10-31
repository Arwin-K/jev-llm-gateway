"""Fifty fixed synthetic HTTP contract cases, never model-quality evidence."""
import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from jev_gateway.api import create_app
from jev_gateway.config import from_env
from jev_gateway.routing.baselines import FixedRouter
from jev_gateway.transport import BackendTransport


def test_fifty_fixed_mocked_regression_prompts():
    fixture = json.loads((Path(__file__).parent / "fixtures" / "ci_prompts.json").read_text())
    cases = fixture["cases"]
    assert len(cases) == 50 and len({case["id"] for case in cases}) == 50
    seen = []

    def backend(request):
        payload = json.loads(request.content)
        seen.append(payload)
        if "Controlled CI prompt 46" in payload["messages"][0]["content"] or any(
            f"Controlled CI prompt {number}" in payload["messages"][0]["content"]
            for number in range(47, 51)):
            return httpx.Response(503)
        return httpx.Response(200, json={"id": "mock", "object": "chat.completion",
                                         "choices": [{"index": 0, "message": {"content": "fixture answer"}}]})

    transport = BackendTransport(2, httpx.MockTransport(backend))
    with TestClient(create_app(from_env(), transport, router=FixedRouter("small"))) as client:
        for case in cases:
            response = client.post("/v1/chat/completions", json={
                "model": case["model"], "execution_mode": case["execution_mode"],
                "max_tokens": case["max_tokens"], "messages": [{"role": "user", "content": case["message"]}]})
            expected = 422 if case["group"] == "over_limit" else 502 if case["group"] == "backend_unavailable" else 200
            assert response.status_code == expected, case["id"]
            if expected == 200:
                assert response.json()["choices"][0]["message"]["content"] == "fixture answer"
                assert response.headers["x-jev-tier"] in {"small", "medium"}
        metrics = client.get("/metrics").text
    assert len(seen) == 45
    assert 'jev_client_requests_total{mode="standard",status="200"} 30.0' in metrics
    assert 'jev_client_requests_total{mode="route_first",status="200"} 10.0' in metrics
    assert 'jev_client_requests_total{mode="standard",status="502"} 5.0' in metrics
    assert 'jev_client_requests_total{mode="standard",status="422"} 5.0' in metrics
