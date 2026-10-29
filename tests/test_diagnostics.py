from jev_gateway.diagnostics import smoke


def test_smoke_reports_unavailable_gateway(capsys):
    assert smoke(gateway_url="http://127.0.0.1:1") == 1
    assert "smoke failed" in capsys.readouterr().out
