"""Typed, explicit runtime configuration. Secrets are read only from environment."""

import os
from datetime import date
from dataclasses import dataclass
from urllib.parse import urlparse


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Backend:
    tier: str
    model: str
    base_url: str
    api_key_env: str | None = None
    max_context_tokens: int = 4096

    def __post_init__(self):
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            raise ConfigError(f"{self.tier} base URL must be an absolute HTTP(S) URL without credentials")
        if self.max_context_tokens < 1:
            raise ConfigError(f"{self.tier} context limit must be positive")
        if not self.model.strip():
            raise ConfigError(f"{self.tier} model is required")

    @property
    def api_key(self):
        return os.environ.get(self.api_key_env, "") if self.api_key_env else ""


@dataclass(frozen=True)
class Settings:
    small: Backend
    medium: Backend
    frontier: Backend
    timeout_seconds: float = 60.0
    max_output_tokens: int = 256
    max_active_requests: int = 8
    max_queued_requests: int = 16
    availability_failover_enabled: bool = False
    frontier_max_requests: int = 0
    frontier_max_tokens: int = 0
    frontier_max_usd: float = 0.0
    frontier_input_usd_per_million: float = 0.0
    frontier_output_usd_per_million: float = 0.0
    router_training_fingerprint: str = ""
    jev_model: str = "UNCONFIGURED"
    jev_max_requests: int = 0
    jev_max_tokens: int = 0
    jev_max_usd: float = 0.0
    jev_input_usd_per_million: float = 0.0
    jev_output_usd_per_million: float = 0.0
    jev_decision_output_tokens: int = 256
    jev_breaker_failures: int = 3
    jev_breaker_cooldown_seconds: float = 30.
    jev_rate_source_url: str = ""
    jev_rate_effective_date: str = ""
    router_policy: str = "jev-choice"
    router_seed: int = 17
    router_artifact: str = ""
    router_thresholds: str = ""
    strands_url: str = ""
    strands_model: str = ""
    strands_checkpoint: str = ""
    strands_device: str = "mps"
    execution_paid_enabled: bool = False
    execution_max_requests: int = 0
    execution_max_tokens: int = 0
    execution_max_usd: float = 0.0
    verification_threshold: float | None = None
    verification_threshold_source: str = ""
    cache_path: str = ""
    cache_embedding_revision: str = ""
    cache_similarity_threshold: float | None = None
    cache_similarity_threshold_source: str = ""
    cache_verification_threshold: float | None = None
    cache_verification_threshold_source: str = ""
    cache_namespace: str = "local"
    cache_ttl_seconds: int = 86400
    cache_similarity_only_enabled: bool = False

    def __post_init__(self):
        if not 0 < self.timeout_seconds <= 300:
            raise ConfigError("timeout_seconds must be between 0 and 300")
        if self.jev_rate_effective_date:
            try:
                date.fromisoformat(self.jev_rate_effective_date)
            except ValueError as exc:
                raise ConfigError("Jev rate effective date must be ISO format") from exc
        if not 1 <= self.max_output_tokens <= 8192:
            raise ConfigError("max_output_tokens must be between 1 and 8192")
        if self.max_active_requests < 1 or self.max_queued_requests < 0:
            raise ConfigError("admission limits must allow active work and a nonnegative queue")
        if (min(self.frontier_max_requests, self.frontier_max_tokens, self.jev_max_requests, self.jev_max_tokens) < 0
            or self.frontier_max_usd < 0 or self.jev_max_usd < 0 or self.jev_decision_output_tokens < 1):
            raise ConfigError("frontier limits cannot be negative")
        if self.execution_max_requests < 0 or self.execution_max_tokens < 0 or self.execution_max_usd < 0:
            raise ConfigError("execution limits cannot be negative")
        if self.jev_breaker_failures < 1 or self.jev_breaker_cooldown_seconds <= 0:
            raise ConfigError("Jev breaker threshold and cooldown must be positive")
        for value, source in ((self.verification_threshold,self.verification_threshold_source),
                              (self.cache_similarity_threshold,self.cache_similarity_threshold_source),
                              (self.cache_verification_threshold,self.cache_verification_threshold_source)):
            if value is not None and (not 0 <= value <= 1 or not source):
                raise ConfigError("configured threshold requires a [0,1] value and source")
        if self.cache_ttl_seconds < 1 or not self.cache_namespace:
            raise ConfigError("cache TTL and namespace must be positive/nonempty")

    @property
    def frontier_enabled(self):
        return bool(self.frontier.model != "UNCONFIGURED" and self.frontier.api_key and self.frontier_max_requests > 0 and
                    self.frontier_max_tokens > 0 and self.frontier_max_usd > 0 and
                    self.frontier_input_usd_per_million > 0 and self.frontier_output_usd_per_million > 0)

    @property
    def jev_enabled(self):
        return bool(self.jev_model != "UNCONFIGURED" and os.getenv("TYPESAFE_API_KEY") and
                    self.jev_max_requests > 0 and self.jev_max_tokens > 0 and self.jev_max_usd > 0 and
                    self.jev_input_usd_per_million > 0 and self.jev_output_usd_per_million > 0 and
                    self.jev_rate_source_url.startswith("https://") and self.jev_rate_effective_date)

    def backend(self, tier):
        if tier not in {"small", "medium", "frontier"}:
            raise ConfigError(f"unknown tier: {tier}")
        return getattr(self, tier)


def from_env():
    def optional_number(name):
        value=os.getenv(name)
        return None if value is None or value == "" else number(name,value)

    def integer(name, default):
        try:
            return int(os.getenv(name, default))
        except ValueError as exc:
            raise ConfigError(f"{name} must be an integer") from exc

    def number(name, default):
        try:
            return float(os.getenv(name, default))
        except ValueError as exc:
            raise ConfigError(f"{name} must be a number") from exc

    return Settings(
        small=Backend("small", os.getenv("JEV_SMALL_MODEL", "qwen2.5:1.5b"), os.getenv("JEV_SMALL_URL", "http://127.0.0.1:11434/v1"), max_context_tokens=integer("JEV_SMALL_CONTEXT_TOKENS", "4096")),
        medium=Backend("medium", os.getenv("JEV_MEDIUM_MODEL", "qwen2.5:7b"), os.getenv("JEV_MEDIUM_URL", "http://127.0.0.1:11434/v1"), max_context_tokens=integer("JEV_MEDIUM_CONTEXT_TOKENS", "4096")),
        frontier=Backend("frontier", os.getenv("JEV_FRONTIER_MODEL") or "UNCONFIGURED", os.getenv("JEV_FRONTIER_URL", "https://api.openai.com/v1"), "JEV_FRONTIER_API_KEY", max_context_tokens=integer("JEV_FRONTIER_CONTEXT_TOKENS", "4096")),
        timeout_seconds=number("JEV_TIMEOUT_SECONDS", "60"),
        max_output_tokens=integer("JEV_MAX_OUTPUT_TOKENS", "256"),
        max_active_requests=integer("JEV_MAX_ACTIVE_REQUESTS", "8"),
        max_queued_requests=integer("JEV_MAX_QUEUED_REQUESTS", "16"),
        availability_failover_enabled=os.getenv("JEV_AVAILABILITY_FAILOVER_ENABLED", "false").lower()=="true",
        frontier_max_requests=integer("JEV_FRONTIER_MAX_REQUESTS", "0"),
        frontier_max_tokens=integer("JEV_FRONTIER_MAX_TOKENS", "0"),
        frontier_max_usd=number("JEV_FRONTIER_MAX_USD", "0"),
        frontier_input_usd_per_million=number("JEV_FRONTIER_INPUT_USD_PER_MILLION", "0"),
        frontier_output_usd_per_million=number("JEV_FRONTIER_OUTPUT_USD_PER_MILLION", "0"),
        router_training_fingerprint=os.getenv("JEV_ROUTER_TRAINING_FINGERPRINT", ""),
        jev_model=os.getenv("JEV_DECISION_MODEL") or "UNCONFIGURED",
        jev_max_requests=integer("JEV_DECISION_MAX_REQUESTS", "0"),
        jev_max_tokens=integer("JEV_DECISION_MAX_TOKENS", "0"),
        jev_max_usd=number("JEV_DECISION_MAX_USD", "0"),
        jev_input_usd_per_million=number("JEV_DECISION_INPUT_USD_PER_MILLION", "0"),
        jev_output_usd_per_million=number("JEV_DECISION_OUTPUT_USD_PER_MILLION", "0"),
        jev_decision_output_tokens=integer("JEV_DECISION_OUTPUT_TOKENS", "256"),
        jev_breaker_failures=integer("JEV_BREAKER_FAILURES", "3"),
        jev_breaker_cooldown_seconds=number("JEV_BREAKER_COOLDOWN_SECONDS", "30"),
        jev_rate_source_url=os.getenv("JEV_DECISION_RATE_SOURCE_URL", ""),
        jev_rate_effective_date=os.getenv("JEV_DECISION_RATE_EFFECTIVE_DATE", ""),
        router_policy=os.getenv("JEV_ROUTER_POLICY", "jev-choice"),
        router_seed=integer("JEV_ROUTER_SEED", "17"),
        router_artifact=os.getenv("JEV_ROUTER_ARTIFACT", ""),
        router_thresholds=os.getenv("JEV_ROUTER_THRESHOLDS", ""),
        strands_url=os.getenv("JEV_STRANDS_URL", ""),
        strands_model=os.getenv("JEV_STRANDS_MODEL", ""),
        strands_checkpoint=os.getenv("JEV_STRANDS_CHECKPOINT", ""),
        strands_device=os.getenv("JEV_STRANDS_DEVICE", "mps"),
        execution_paid_enabled=os.getenv("JEV_EXECUTION_PAID_ENABLED", "false").lower()=="true",
        execution_max_requests=integer("JEV_EXECUTION_MAX_REQUESTS", "0"),
        execution_max_tokens=integer("JEV_EXECUTION_MAX_TOKENS", "0"),
        execution_max_usd=number("JEV_EXECUTION_MAX_USD", "0"),
        verification_threshold=optional_number("JEV_VERIFICATION_THRESHOLD"),
        verification_threshold_source=os.getenv("JEV_VERIFICATION_THRESHOLD_SOURCE", ""),
        cache_path=os.getenv("JEV_CACHE_PATH", ""),
        cache_embedding_revision=os.getenv("JEV_CACHE_EMBEDDING_REVISION", ""),
        cache_similarity_threshold=optional_number("JEV_CACHE_SIMILARITY_THRESHOLD"),
        cache_similarity_threshold_source=os.getenv("JEV_CACHE_SIMILARITY_THRESHOLD_SOURCE", ""),
        cache_verification_threshold=optional_number("JEV_CACHE_VERIFICATION_THRESHOLD"),
        cache_verification_threshold_source=os.getenv("JEV_CACHE_VERIFICATION_THRESHOLD_SOURCE", ""),
        cache_namespace=os.getenv("JEV_CACHE_NAMESPACE", "local"),
        cache_ttl_seconds=integer("JEV_CACHE_TTL_SECONDS", "86400"),
        cache_similarity_only_enabled=os.getenv("JEV_CACHE_SIMILARITY_ONLY_ENABLED", "false").lower()=="true",
    )
