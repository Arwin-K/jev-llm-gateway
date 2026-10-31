import subprocess
import sys


BASE = [sys.executable, "load/run.py", "--scenario", "steady", "--base-users", "1",
        "--max-requests", "10", "--max-tokens", "320", "--output-tokens", "32",
        "--placement", "mac-host", "--model-condition", "unverified",
        "--output", "runs/day5-dryrun-test"]


def test_paid_mix_refuses_traffic_without_positive_gates():
    result = subprocess.run(BASE + ["--mix", '{"frontier":1.0}'], capture_output=True, text=True)
    assert result.returncode != 0
    assert "paid-capable workloads need explicit enablement" in result.stderr


def test_dry_run_describes_closed_loop_and_creates_no_output():
    result = subprocess.run(BASE, capture_output=True, text=True)
    assert result.returncode == 0
    assert '"arrival_model": "closed_loop_users"' in result.stdout
    assert '"status": "pending"' in result.stdout
