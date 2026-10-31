"""Bounded in-cluster API traffic while replacing one project gateway pod."""
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


NAMESPACE = "jev-gateway"
CLUSTER = "kind-jev-gateway-day5"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kubeconfig", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--interval", type=float, default=.2)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.requests < 2 or args.requests > 500 or not 0 <= args.interval <= 10 or args.output.exists():
        parser.error("use 2-500 requests, a bounded interval, and a new output path")
    base = ["kubectl", "--kubeconfig", str(args.kubeconfig)]
    context = subprocess.check_output(base + ["config", "current-context"], text=True).strip()
    if context != CLUSTER:
        parser.error("kubeconfig does not select the project kind cluster")
    pods = json.loads(subprocess.check_output(base + ["-n", NAMESPACE, "get", "pods",
                        "-l", "app=jev-gateway", "-o", "json"], text=True))["items"]
    ready = sorted(pod["metadata"]["name"] for pod in pods
                   if pod["status"].get("phase") == "Running" and
                   any(condition.get("type") == "Ready" and condition.get("status") == "True"
                       for condition in pod["status"].get("conditions", [])))
    if len(ready) < 2:
        parser.error("two ready project gateway pods are required")
    client, target = ready[:2]
    plan = {"run_id": datetime.now(timezone.utc).strftime("day5-pod-%Y%m%dT%H%M%SZ"),
            "context": context, "namespace": NAMESPACE, "client_pod": client,
            "deleted_pod": target, "requests_planned": args.requests,
            "interval_seconds": args.interval, "endpoint": "GET /v1/models",
            "backend_inference": False, "status": "pending"}
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    code = """import json,time,urllib.request
from datetime import datetime,timezone
for i in range(REQUESTS):
    started=time.monotonic()
    try:
        with urllib.request.urlopen('http://jev-gateway.jev-gateway.svc.cluster.local:8080/v1/models',timeout=3) as response:
            item={'index':i,'at':datetime.now(timezone.utc).isoformat(),'status':response.status,'elapsed_ms':(time.monotonic()-started)*1000}
    except Exception as exc:
        item={'index':i,'at':datetime.now(timezone.utc).isoformat(),'error':type(exc).__name__,'elapsed_ms':(time.monotonic()-started)*1000}
    print(json.dumps(item),flush=True)
    time.sleep(INTERVAL)
""".replace("REQUESTS", str(args.requests)).replace("INTERVAL", str(args.interval))
    started = time.monotonic()
    plan["started_at"] = stamp()
    process = subprocess.Popen(base + ["-n", NAMESPACE, "exec", client, "--", "python", "-c", code],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(max(.5, min(2., args.requests * args.interval / 5)))
    plan["delete_requested_at"] = stamp()
    deletion = subprocess.run(base + ["-n", NAMESPACE, "delete", "pod", target, "--wait=false"],
                              capture_output=True, text=True, check=False)
    plan["delete_exit_code"] = deletion.returncode
    timeline = []
    while process.poll() is None and time.monotonic() - started < args.requests * (args.interval + 4) + 20:
        snapshot = json.loads(subprocess.check_output(base + ["-n", NAMESPACE, "get", "pods",
                             "-l", "app=jev-gateway", "-o", "json"], text=True))
        timeline.append({"at": stamp(), "ready_pods": sorted(pod["metadata"]["name"]
                         for pod in snapshot["items"] if any(
                         condition.get("type") == "Ready" and condition.get("status") == "True"
                         for condition in pod["status"].get("conditions", [])))})
        time.sleep(.5)
    stdout, stderr = process.communicate(timeout=10)
    events = [json.loads(line) for line in stdout.splitlines() if line.startswith("{")]
    plan.update({"status": "finished" if process.returncode == 0 and deletion.returncode == 0 else "failed",
                 "finished_at": stamp(), "actual_duration_seconds": time.monotonic() - started,
                 "client_exit_code": process.returncode,
                 "client_error": stderr[-300:] if stderr else None,
                 "responses": events, "pod_timeline": timeline,
                 "http_200": sum(item.get("status") == 200 for item in events),
                 "request_errors": sum(item.get("status") != 200 for item in events)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n")
    print(json.dumps({key: plan[key] for key in ("run_id", "status", "http_200", "request_errors",
                                               "actual_duration_seconds")}, indent=2))


if __name__ == "__main__":
    main()
