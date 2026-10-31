"""Process-local Prometheus text metrics with fixed, low-cardinality dimensions."""
from collections import defaultdict
import threading

from fastapi.responses import PlainTextResponse


BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300)
TIERS = {"small", "medium", "frontier"}
MODES = {"standard", "route_first", "cascade", "hybrid"}


def bounded(value, choices):
    return value if value in choices else "other"


class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.counters = defaultdict(float)
        self.histograms = {}
        self.active = 0
        self.queued = 0
        self.breaker_state = 0

    def inc(self, name, labels=(), value=1):
        with self.lock:
            self.counters[(name, labels)] += value

    def observe(self, name, seconds, labels=()):
        with self.lock:
            histogram = self.histograms.setdefault((name, labels), {"count": 0, "sum": 0.,
                                                                   "buckets": [0] * len(BUCKETS)})
            seconds = max(0, seconds)
            histogram["count"] += 1
            histogram["sum"] += seconds
            for index, bucket in enumerate(BUCKETS):
                if seconds <= bucket:
                    histogram["buckets"][index] += 1

    def start_request(self):
        with self.lock:
            self.active += 1

    def end_request(self, mode, status, elapsed):
        with self.lock:
            self.active -= 1
        self.inc("jev_client_requests_total", (bounded(mode, MODES), str(status)))
        self.observe("jev_request_duration_seconds", elapsed, (bounded(mode, MODES),))

    def trace(self, record):
        tier = bounded(record.get("tier"), TIERS)
        if tier != "other":
            self.inc("jev_selected_tier_total", (tier,))
        routing = record.get("routing") or {}
        if routing:
            self.inc("jev_routing_decisions_total", (
                bounded(routing.get("outcome"), {"selected", "fallback_selected", "failed"}),
                "yes" if routing.get("fallback_reason") else "no"))
            if isinstance(routing.get("duration_ms"), (int, float)):
                self.observe("jev_stage_duration_seconds", routing["duration_ms"] / 1000, ("routing",))
        execution = record.get("execution") or {}
        cache = execution.get("cache", "off")
        cache_label = (cache if cache in {"off", "miss", "verified_hit", "similarity_only_hit",
                                      "inserted", "unavailable", "candidate_ineligible"}
                       else "rejected_or_error")
        self.inc("jev_cache_outcomes_total", (cache_label,))
        for attempt in execution.get("attempts", []):
            self.inc("jev_generation_attempts_total", (
                bounded(attempt.get("tier"), TIERS),
                bounded(attempt.get("outcome"), {"generated", "generation_error", "accepted_verified",
                                                         "unverified_route_first", "verification_failed", "rejected", "skipped"})))
            if isinstance(attempt.get("duration_ms"), (int, float)) and attempt.get("outcome") != "skipped":
                self.observe("jev_stage_duration_seconds", attempt["duration_ms"] / 1000, ("generation",))
            if attempt.get("outcome") in {"accepted_verified", "verification_failed", "rejected"}:
                self.inc("jev_verification_outcomes_total", (attempt["outcome"],))
        for stage in execution.get("stages", []):
            stage_name = bounded(stage.get("stage"), {"routing", "generation", "verification", "cache_verification"})
            if stage_name != "other":
                self.inc("jev_stage_reservations_total", (stage_name,))
        if isinstance(execution.get("reserved_usd"), (int, float)):
            self.inc("jev_estimated_reserved_usd_total", value=execution["reserved_usd"])
            self.inc("jev_cost_coverage_total", ("estimated_reservation",))
        else:
            self.inc("jev_cost_coverage_total", ("unknown",))
        usage = record.get("usage") or {}
        for key in ("prompt_tokens", "completion_tokens"):
            if isinstance(usage.get(key), int) and usage[key] >= 0:
                self.inc("jev_known_tokens_total", (key,), usage[key])

    def render(self):
        with self.lock:
            counters = dict(self.counters)
            histograms = {key: {"count": value["count"], "sum": value["sum"],
                                "buckets": list(value["buckets"])}
                          for key, value in self.histograms.items()}
            active, queued, breaker_state = self.active, self.queued, self.breaker_state
        lines = ["# TYPE jev_active_requests gauge", f"jev_active_requests {active}",
                 "# TYPE jev_queued_requests gauge", f"jev_queued_requests {queued}",
                 "# TYPE jev_breaker_state gauge", f"jev_breaker_state {breaker_state}"]
        names = {
            "jev_client_requests_total": ("mode", "status"),
            "jev_selected_tier_total": ("tier",),
            "jev_routing_decisions_total": ("outcome", "fallback"),
            "jev_cache_outcomes_total": ("outcome",),
            "jev_generation_attempts_total": ("tier", "outcome"),
            "jev_verification_outcomes_total": ("outcome",),
            "jev_stage_reservations_total": ("stage",),
            "jev_estimated_reserved_usd_total": (),
            "jev_cost_coverage_total": ("status",),
            "jev_known_tokens_total": ("kind",),
            "jev_admission_rejections_total": ("reason",),
            "jev_breaker_transitions_total": ("state",),
        }
        for name, keys in names.items():
            lines.append(f"# TYPE {name} counter")
            for (metric, labels), value in sorted(counters.items()):
                if metric == name:
                    fields = ",".join(f'{key}="{value_}"' for key, value_ in zip(keys, labels))
                    lines.append(f"{name}{{{fields}}} {value}" if fields else f"{name} {value}")
        for name, keys in (("jev_request_duration_seconds", ("mode",)),
                           ("jev_stage_duration_seconds", ("stage",)),
                           ("jev_first_output_seconds", ())):
            lines.append(f"# TYPE {name} histogram")
            for (metric, labels), values in sorted(histograms.items()):
                if metric != name:
                    continue
                fields = ",".join(f'{key}="{value_}"' for key, value_ in zip(keys, labels))
                prefix = fields + "," if fields else ""
                for bucket, count in zip(BUCKETS, values["buckets"]):
                    lines.append(f'{name}_bucket{{{prefix}le="{bucket}"}} {count}')
                lines.append(f'{name}_bucket{{{prefix}le="+Inf"}} {values["count"]}')
                suffix = "{" + fields + "}" if fields else ""
                lines.extend((f"{name}_sum{suffix} {values['sum']}",
                              f"{name}_count{suffix} {values['count']}"))
        return "\n".join(lines) + "\n"


def metrics_response(metrics):
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4; charset=utf-8")
