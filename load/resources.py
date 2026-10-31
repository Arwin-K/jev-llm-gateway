"""Best-effort raw Docker resource sampling for a local gateway container."""
import json
import subprocess
import threading
from datetime import datetime, timezone


def sample(container, output, stop: threading.Event, interval=30.):
    with output.open("a") as stream:
        while not stop.is_set():
            observed_at = datetime.now(timezone.utc).isoformat()
            command = ["docker", "stats", "--no-stream", "--format", "{{json .}}", container]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
                payload = {"observed_at": observed_at, "exit_code": result.returncode,
                           "raw": result.stdout.strip(), "error": result.stderr.strip()[:200]}
            except (OSError, subprocess.TimeoutExpired) as exc:
                payload = {"observed_at": observed_at, "error": type(exc).__name__}
            stream.write(json.dumps(payload) + "\n")
            stream.flush()
            stop.wait(interval)
