from laya_gateway import diagnostics


def test_smoke_reports_native_runtime_error(monkeypatch, capsys):
    async def fail(*args, **kwargs):
        raise RuntimeError("checkpoint missing")

    monkeypatch.setattr(diagnostics, "complete_local", fail)
    assert diagnostics.smoke("auto") == 1
    assert "RuntimeError" in capsys.readouterr().out


def test_doctor_succeeds_when_laya_and_local_tiers_are_available(monkeypatch, capsys):
    async def report():
        return {
            "decision": {"provider": "native-laya", "available": True},
            "tiers": {"small": {"installed": True}, "medium": {"installed": True}},
        }

    monkeypatch.setattr(diagnostics, "_doctor", report)
    assert diagnostics.doctor() == 0
    assert '"provider": "native-laya"' in capsys.readouterr().out


def test_doctor_fails_when_laya_checkpoint_is_unavailable(monkeypatch, capsys):
    async def report():
        return {
            "decision": {"provider": "native-laya", "available": False},
            "tiers": {"small": {"installed": True}, "medium": {"installed": True}},
        }

    monkeypatch.setattr(diagnostics, "_doctor", report)
    assert diagnostics.doctor() == 1
    assert '"available": false' in capsys.readouterr().out
