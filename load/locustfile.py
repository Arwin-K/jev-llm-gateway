"""Single-process bounded gateway workloads; no held-out benchmark prompts."""
import json
import os
import threading

from locust import HttpUser, LoadTestShape, between, task


SCENARIO = os.environ["JEV_LOAD_SCENARIO"]
BASE_USERS = int(os.environ["JEV_LOAD_USERS"])
MAX_REQUESTS = int(os.environ["JEV_LOAD_MAX_REQUESTS"])
MAX_TOKENS = int(os.environ["JEV_LOAD_MAX_TOKENS"])
OUTPUT_TOKENS = int(os.environ["JEV_LOAD_OUTPUT_TOKENS"])
MIX = json.loads(os.environ["JEV_LOAD_MIX"])
STREAM = os.environ["JEV_LOAD_STREAM"] == "true"
MODE = os.environ["JEV_LOAD_EXECUTION_MODE"]
CACHE = os.environ["JEV_LOAD_CACHE_MODE"]
WAIT = float(os.environ["JEV_LOAD_WAIT_SECONDS"])
_lock = threading.Lock()
_requests = 0
_reserved_tokens = 0


def reserve():
    global _requests, _reserved_tokens
    with _lock:
        if _requests >= MAX_REQUESTS or _reserved_tokens + OUTPUT_TOKENS > MAX_TOKENS:
            return False
        _requests += 1
        _reserved_tokens += OUTPUT_TOKENS
        return True


class GatewayUser(HttpUser):
    wait_time = between(WAIT, WAIT)

    @task
    def chat(self):
        if not reserve():
            self.environment.runner.quit()
            return
        # Deterministic mix by process-local attempt number; no private text in labels.
        with _lock:
            fraction = ((_requests - 1) % 100) / 100
        running = 0.
        tier = "small"
        for candidate, weight in MIX.items():
            running += weight
            if fraction < running:
                tier = candidate
                break
        payload = {"model": tier, "messages": [{"role": "user", "content":
                   "Answer briefly: what is two plus two?"}], "max_tokens": OUTPUT_TOKENS,
                   "stream": STREAM, "execution_mode": MODE, "cache_mode": CACHE}
        with self.client.post("/v1/chat/completions", json=payload, name=f"chat:{tier}:{MODE}:{CACHE}",
                              catch_response=True, stream=STREAM, timeout=90) as response:
            if STREAM:
                for _ in response.iter_content(chunk_size=4096):
                    pass
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")


class GatewayShape(LoadTestShape):
    def tick(self):
        elapsed = self.get_run_time()
        if SCENARIO == "steady":
            return (BASE_USERS, max(1, BASE_USERS)) if elapsed < 600 else None
        if SCENARIO == "soak":
            return (BASE_USERS, max(1, BASE_USERS)) if elapsed < 3600 else None
        if elapsed < 120:
            return BASE_USERS, max(1, BASE_USERS)
        if elapsed < 240:
            return BASE_USERS * 5, max(1, BASE_USERS * 5)
        if elapsed < 360:
            return BASE_USERS, max(1, BASE_USERS * 5)
        return None
