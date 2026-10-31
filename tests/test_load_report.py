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
