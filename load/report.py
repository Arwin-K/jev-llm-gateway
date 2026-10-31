"""Summarize observed Locust output without treating a planned run as completed."""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def summarize(path: Path):
    manifest = json.loads((path / "manifest.json").read_text())
    result = {"run_id": manifest["run_id"], "scenario": manifest["scenario"],
              "status": manifest["status"], "planned_duration_seconds": manifest["duration_seconds"],
              "arrival_model": manifest["arrival_model"]}
    if "started_at" not in manifest or "finished_at" not in manifest:
        result["evidence_state"] = "pending_or_interrupted_without_final_time"
        return result
    duration = (datetime.fromisoformat(manifest["finished_at"]) -
                datetime.fromisoformat(manifest["started_at"])).total_seconds()
    result["actual_duration_seconds"] = duration
    rows = read_rows(path / "locust_stats.csv")
    aggregate = next((row for row in rows if row.get("Name") == "Aggregated"), None)
    if aggregate is None:
        result["evidence_state"] = "missing_aggregate_stats"
        return result
    count = int(aggregate["Request Count"])
    failures = int(aggregate["Failure Count"])
    result.update({"requests": count, "failures": failures,
                   "achieved_requests_per_second": count / duration if duration > 0 else None,
                   "failure_fraction": failures / count if count else None,
                   "median_response_ms": float(aggregate["Median Response Time"]),
                   "p95_response_ms": float(aggregate["95%"]) if aggregate.get("95%") else None,
                   "p99_response_ms": float(aggregate["99%"]) if aggregate.get("99%") else None,
                   "evidence_state": "complete_interval" if duration >= manifest["duration_seconds"]
                   else "shorter_than_planned"})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.run), indent=2))


if __name__ == "__main__":
    main()
