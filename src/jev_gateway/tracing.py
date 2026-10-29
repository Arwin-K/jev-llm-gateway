"""Secret-free structured request traces."""

import json
import logging
import time
import uuid
from datetime import datetime, timezone


logger = logging.getLogger("jev_gateway.trace")


class RequestTrace:
    def __init__(self, tier: str, backend_model: str):
        self.request_id = uuid.uuid4().hex
        self.started_monotonic = time.monotonic()
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.tier = tier
        self.backend_model = backend_model

    def finish(self, status: str, usage: dict | None = None, cost_status: str = "unknown"):
        record = {
            "request_id": self.request_id,
            "started_at": self.started_at,
            "duration_ms": round((time.monotonic() - self.started_monotonic) * 1000, 3),
            "tier": self.tier,
            "backend_model": self.backend_model,
            "status": status,
            "usage": {key: usage.get(key) for key in ("prompt_tokens", "completion_tokens", "total_tokens")} if usage else None,
            "cost_status": cost_status,
        }
        logger.info(json.dumps(record, separators=(",", ":")))
        return record
