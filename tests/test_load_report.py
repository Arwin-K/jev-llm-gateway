import csv
import importlib.util
import json
from pathlib import Path

module = importlib.util.spec_from_file_location("day5_load_report", Path(__file__).parents[1] / "load" / "report.py")
load_report = importlib.util.module_from_spec(module)
module.loader.exec_module(load_report)
summarize = load_report.summarize


def test_short_steady_run_is_not_reported_as_ten_minutes(tmp_path: Path):
    (tmp_path / "manifest.json").write_text(json.dumps({
        "run_id": "fixture", "scenario": "steady", "status": "finished",
        "duration_seconds": 600, "arrival_model": "closed_loop_users",
        "started_at": "2026-10-31T12:00:00+00:00",
        "finished_at": "2026-10-31T12:01:00+00:00"}))
    with (tmp_path / "locust_stats.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, ["Name", "Request Count", "Failure Count",
                                          "Median Response Time", "95%", "99%"])
        writer.writeheader()
        writer.writerow({"Name": "Aggregated", "Request Count": 30, "Failure Count": 3,
                         "Median Response Time": 20, "95%": 70, "99%": 90})
    report = summarize(tmp_path)
    assert report["actual_duration_seconds"] == 60
    assert report["achieved_requests_per_second"] == .5
    assert report["evidence_state"] == "shorter_than_planned"


def test_spike_ratio_uses_observed_rates_not_user_multiplier(tmp_path: Path):
    (tmp_path / "manifest.json").write_text(json.dumps({
        "run_id": "fixture", "scenario": "spike", "status": "finished",
        "duration_seconds": 360, "arrival_model": "closed_loop_users",
        "started_at": "2026-10-31T12:00:00+00:00",
        "finished_at": "2026-10-31T12:06:00+00:00"}))
    with (tmp_path / "locust_stats.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, ["Name", "Request Count", "Failure Count",
                                          "Median Response Time", "95%", "99%"])
        writer.writeheader()
        writer.writerow({"Name": "Aggregated", "Request Count": 600, "Failure Count": 0,
                         "Median Response Time": 20, "95%": 70, "99%": 90})
    start = 1793448000
    with (tmp_path / "locust_stats_history.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, ["Name", "Timestamp", "Requests/s", "Failures/s", "User Count"])
        writer.writeheader()
        for offset, rate, users in ((60, 2, 1), (180, 6, 5), (300, 2, 1)):
            writer.writerow({"Name": "Aggregated", "Timestamp": start + offset,
                             "Requests/s": rate, "Failures/s": 0, "User Count": users})
    spike = summarize(tmp_path)["spike"]
    assert spike["mean_observed_users"]["spike"] == 5
    assert spike["rate_ratio"] == 3
    assert spike["fivefold_rate_observed"] is False


def test_soak_resource_summary_keeps_actual_sample_count(tmp_path: Path):
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("resource_report", Path(__file__).parents[1] / "load" / "report.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "gateway-resources.jsonl"
    path.write_text("\n".join(json.dumps({"exit_code": 0, "raw": json.dumps({"MemUsage": value})})
                              for value in ("100MiB / 8GiB", "110MiB / 8GiB")) + "\n")
    result = module.summarize_resources(path)
    assert result == {"samples": 2, "memory_mib": {"first": 100, "last": 110, "maximum": 110}}
