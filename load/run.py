"""Validate and launch an explicitly bounded single-process Locust experiment."""
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=("steady", "spike", "soak"), required=True)
    parser.add_argument("--host", default="http://127.0.0.1:8080")
    parser.add_argument("--base-users", type=int, required=True)
    parser.add_argument("--max-requests", type=int, required=True)
    parser.add_argument("--max-tokens", type=int, required=True)
    parser.add_argument("--output-tokens", type=int, default=32)
    parser.add_argument("--max-usd", type=float, default=0.)
    parser.add_argument("--paid-enabled", action="store_true")
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--execution-mode", choices=("standard", "route_first", "cascade", "hybrid"), default="standard")
    parser.add_argument("--cache-mode", choices=("off", "verified", "similarity_only"), default="off")
    parser.add_argument("--mix", default='{"small":1.0}')
    parser.add_argument("--wait-seconds", type=float, default=1.)
    parser.add_argument("--placement", required=True)
    parser.add_argument("--model-condition", choices=("cold", "warm", "unverified"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    mix = json.loads(args.mix)
    if (args.base_users < 1 or args.max_requests < 1 or args.max_tokens < 1 or
        args.output_tokens < 1 or args.wait_seconds < 0 or args.max_usd < 0 or
        not mix or set(mix) - {"small", "medium", "frontier", "auto"} or
        any(not isinstance(weight, (int, float)) or weight <= 0 for weight in mix.values()) or
        abs(sum(mix.values()) - 1.) > 1e-9):
        parser.error("positive limits and a normalized eligible request mix are required")
    if args.stream and (args.execution_mode != "standard" or args.cache_mode != "off"):
        parser.error("streaming is supported only for standard execution without cache")
    uses_paid = ("frontier" in mix or args.execution_mode in {"cascade", "hybrid"} or
                 args.cache_mode == "verified" or "auto" in mix and os.getenv("JEV_ROUTER_POLICY", "jev-choice").startswith("jev-"))
    if uses_paid and (not args.paid_enabled or args.max_usd <= 0):
        parser.error("paid-capable workloads need explicit enablement and positive USD cap")
    if uses_paid:
        # The gateway remains the spending enforcer. This runner verifies the same
        # process-local caps are explicitly configured before launching traffic.
        for name in ("JEV_EXECUTION_MAX_REQUESTS", "JEV_EXECUTION_MAX_TOKENS", "JEV_EXECUTION_MAX_USD"):
            if float(os.getenv(name, "0")) <= 0:
                parser.error(f"{name} must be positive for paid-capable load")
        if os.getenv("JEV_EXECUTION_PAID_ENABLED", "false").lower() != "true":
            parser.error("JEV_EXECUTION_PAID_ENABLED must be true for paid-capable load")
        if args.max_usd > float(os.environ["JEV_EXECUTION_MAX_USD"]):
            parser.error("run USD cap must not exceed the gateway process USD cap")
        for name in (("JEV_FRONTIER_MAX_USD",) if "frontier" in mix else ()) + (
            ("JEV_DECISION_MAX_USD",) if args.execution_mode in {"cascade", "hybrid"} or
            args.cache_mode == "verified" or "auto" in mix else ()):
            configured = float(os.getenv(name, "0"))
            if configured <= 0 or configured > args.max_usd:
                parser.error(f"{name} must be positive and no greater than the run USD cap")
    if args.max_requests * args.output_tokens > args.max_tokens:
        parser.error("max-tokens must cover all planned output reservations")
    if args.output.exists():
        parser.error("output run directory already exists")
    run_id = datetime.now(timezone.utc).strftime("day5-%Y%m%dT%H%M%SZ")
    manifest = {"run_id": run_id, "scenario": args.scenario, "host": args.host,
                "base_users": args.base_users, "requested_multiplier": 5 if args.scenario == "spike" else 1,
                "duration_seconds": {"steady": 600, "spike": 360, "soak": 3600}[args.scenario],
                "max_requests": args.max_requests, "max_tokens": args.max_tokens,
                "output_tokens": args.output_tokens, "max_usd": args.max_usd,
                "paid_enabled": args.paid_enabled, "stream": args.stream,
                "execution_mode": args.execution_mode, "cache_mode": args.cache_mode,
                "mix": mix, "wait_seconds": args.wait_seconds,
                "placement": args.placement, "model_condition": args.model_condition,
                "arrival_model": "closed_loop_users", "status": "pending"}
    if not args.execute:
        print(json.dumps(manifest, indent=2))
        return
    args.output.mkdir(parents=True)
    manifest["status"] = "started"
    manifest["started_at"] = datetime.now(timezone.utc).isoformat()
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    env = dict(os.environ)
    env.update({"JEV_LOAD_SCENARIO": args.scenario, "JEV_LOAD_USERS": str(args.base_users),
                "JEV_LOAD_MAX_REQUESTS": str(args.max_requests), "JEV_LOAD_MAX_TOKENS": str(args.max_tokens),
                "JEV_LOAD_OUTPUT_TOKENS": str(args.output_tokens), "JEV_LOAD_MIX": json.dumps(mix),
                "JEV_LOAD_STREAM": str(args.stream).lower(), "JEV_LOAD_EXECUTION_MODE": args.execution_mode,
                "JEV_LOAD_CACHE_MODE": args.cache_mode, "JEV_LOAD_WAIT_SECONDS": str(args.wait_seconds)})
    command = ["locust", "-f", str(Path(__file__).with_name("locustfile.py")), "--headless",
               "--host", args.host, "--csv", str(args.output / "locust"), "--csv-full-history"]
    with (args.output / "locust.log").open("w") as log:
        completed = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
    manifest["status"] = "finished" if completed.returncode == 0 else "interrupted_or_failed"
    manifest["exit_code"] = completed.returncode
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
