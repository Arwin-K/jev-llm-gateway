from fastapi.testclient import TestClient
from jev_gateway.api import create_app


def test_health_models_and_rejected_input():
    client = TestClient(create_app())
    assert client.get("/healthz").json() == {"status": "ok"}
    assert len(client.get("/v1/models").json()["data"]) == 3
    url = "/v1/chat/completions"
    assert client.post(url, json={"model": "auto", "messages": [{"role": "user", "content": "hi"}]}).status_code == 503
    assert client.post(url, json={"model": "small", "messages": [{"role": "user", "content": [{"type": "image_url"}]}]}).status_code == 422
    assert client.post(url, json={"model": "frontier", "messages": [{"role": "user", "content": "hi"}]}).status_code == 503
