import json
from jev_gateway.tracing import RequestTrace


def test_secret_free_trace(caplog):
    caplog.set_level("INFO", logger="jev_gateway.trace")
    trace = RequestTrace("small", "qwen2.5:1.5b")
    record = trace.finish("ok", {"prompt_tokens": 2, "completion_tokens": 3, "secret": "never-log"})
    assert record["usage"]["total_tokens"] is None
    assert "never-log" not in caplog.text
    assert json.loads(caplog.records[-1].message)["request_id"] == trace.request_id
