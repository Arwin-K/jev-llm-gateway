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
    if manifest["scenario"] == "spike":
        result["spike"] = summarize_spike(path, manifest)
    return result


def summarize_spike(path: Path, manifest):
    started = datetime.fromisoformat(manifest["started_at"]).timestamp()
    phases = {"baseline": [], "spike": [], "recovery": []}
    users = {phase: [] for phase in phases}
    failures = {phase: [] for phase in phases}
    for row in read_rows(path / "locust_stats_history.csv"):
        if row.get("Name") != "Aggregated":
            continue
        try:
            try:
                stamp = float(row["Timestamp"])
            except ValueError:
                stamp = datetime.fromisoformat(row["Timestamp"]).timestamp()
            elapsed = stamp - started
            rate = float(row["Requests/s"])
            failure_rate = float(row["Failures/s"])
            user_count = int(row["User Count"])
        except (KeyError, TypeError, ValueError):
            continue
        phase = "baseline" if elapsed < 120 else "spike" if elapsed < 240 else "recovery" if elapsed < 360 else None
        if phase is not None and elapsed >= 0:
            phases[phase].append(rate)
            users[phase].append(user_count)
            failures[phase].append(failure_rate)
    mean_rates = {phase: sum(values) / len(values) if values else None for phase, values in phases.items()}
    mean_users = {phase: sum(values) / len(values) if values else None for phase, values in users.items()}
    mean_failures = {phase: sum(values) / len(values) if values else None for phase, values in failures.items()}
    baseline, spike = mean_rates["baseline"], mean_rates["spike"]
    ratio = spike / baseline if baseline and spike is not None else None
    return {"mean_observed_requests_per_second": mean_rates,
            "mean_observed_users": mean_users,
            "mean_observed_failures_per_second": mean_failures,
            "rate_ratio": ratio,
            "fivefold_rate_observed": ratio >= 5 if ratio is not None else None,
            "phase_sample_counts": {phase: len(values) for phase, values in phases.items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.run), indent=2))


if __name__ == "__main__":
    main()
