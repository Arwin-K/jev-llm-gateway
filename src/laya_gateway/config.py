"""Native Laya and local-model configuration; secrets are read only from the environment."""
import os
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
    require_trained_fallback: bool = False
    frontier_max_requests: int = 0
    frontier_max_tokens: int = 0
    frontier_max_usd: float = 0.0
    frontier_input_usd_per_million: float = 0.0
    frontier_output_usd_per_million: float = 0.0
    router_training_fingerprint: str = ""
    laya_model: str = "typed-decisions"
    laya_max_requests: int = 100
    laya_max_input_units: int = 200000
    laya_device: str = "mps"
    laya_revision: str = "reviewed"
    router_policy: str = "laya-choice"
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
        if not self.laya_model.strip() or self.laya_max_requests < 0 or self.laya_max_input_units < 0:
            raise ConfigError("Laya model and nonnegative request/input caps are required")
        if not 0 < self.timeout_seconds <= 300:
            raise ConfigError("timeout_seconds must be between 0 and 300")
        if not 1 <= self.max_output_tokens <= 8192:
            raise ConfigError("max_output_tokens must be between 1 and 8192")
        if self.max_active_requests < 1 or self.max_queued_requests < 0:
            raise ConfigError("admission limits must allow active work and a nonnegative queue")
        if min(self.frontier_max_requests, self.frontier_max_tokens) < 0 or self.frontier_max_usd < 0:
            raise ConfigError("frontier limits cannot be negative")
        if min(self.frontier_input_usd_per_million, self.frontier_output_usd_per_million) < 0:
            raise ConfigError("frontier rates cannot be negative")
        if self.execution_max_requests < 0 or self.execution_max_tokens < 0 or self.execution_max_usd < 0:
            raise ConfigError("execution limits cannot be negative")
        for value, source in ((self.verification_threshold, self.verification_threshold_source),
                              (self.cache_similarity_threshold, self.cache_similarity_threshold_source),
                              (self.cache_verification_threshold, self.cache_verification_threshold_source)):
            if value is not None and (not 0 <= value <= 1 or not source):
                raise ConfigError("configured threshold requires a [0,1] value and source")
        if self.cache_ttl_seconds < 1 or not self.cache_namespace:
            raise ConfigError("cache TTL and namespace must be positive/nonempty")

    @property
    def frontier_enabled(self):
        return bool(self.frontier.model != "UNCONFIGURED" and self.frontier.api_key and
                    self.frontier_max_requests > 0 and self.frontier_max_tokens > 0 and
                    self.frontier_max_usd > 0 and self.frontier_input_usd_per_million > 0 and
                    self.frontier_output_usd_per_million > 0)

    @property
    def decision_enabled(self):
        return bool(self.laya_model and self.laya_max_requests > 0 and self.laya_max_input_units > 0)

    def backend(self, tier):
        if tier not in {"small", "medium", "frontier"}:
            raise ConfigError(f"unknown tier: {tier}")
        return getattr(self, tier)


def from_env():
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

    def optional_number(name):
        value = os.getenv(name)
        return None if value in (None, "") else number(name, value)

    prefix = "LAYA_GATEWAY_"
    return Settings(
        small=Backend("small", os.getenv(prefix + "SMALL_MODEL", "qwen2.5:1.5b"),
                      os.getenv(prefix + "SMALL_URL", "http://127.0.0.1:11434/v1"),
                      max_context_tokens=integer(prefix + "SMALL_CONTEXT_TOKENS", "4096")),
        medium=Backend("medium", os.getenv(prefix + "MEDIUM_MODEL", "qwen2.5:7b"),
                       os.getenv(prefix + "MEDIUM_URL", "http://127.0.0.1:11434/v1"),
                       max_context_tokens=integer(prefix + "MEDIUM_CONTEXT_TOKENS", "4096")),
        frontier=Backend("frontier", os.getenv(prefix + "FRONTIER_MODEL") or "UNCONFIGURED",
                         os.getenv(prefix + "FRONTIER_URL", "https://api.openai.com/v1"),
                         prefix + "FRONTIER_API_KEY",
                         max_context_tokens=integer(prefix + "FRONTIER_CONTEXT_TOKENS", "4096")),
        timeout_seconds=number(prefix + "TIMEOUT_SECONDS", "60"),
        max_output_tokens=integer(prefix + "MAX_OUTPUT_TOKENS", "256"),
        max_active_requests=integer(prefix + "MAX_ACTIVE_REQUESTS", "8"),
        max_queued_requests=integer(prefix + "MAX_QUEUED_REQUESTS", "16"),
        availability_failover_enabled=os.getenv(prefix + "AVAILABILITY_FAILOVER_ENABLED", "false").lower() == "true",
        require_trained_fallback=os.getenv(prefix + "REQUIRE_TRAINED_FALLBACK", "false").lower() == "true",
        frontier_max_requests=integer(prefix + "FRONTIER_MAX_REQUESTS", "0"),
        frontier_max_tokens=integer(prefix + "FRONTIER_MAX_TOKENS", "0"),
        frontier_max_usd=number(prefix + "FRONTIER_MAX_USD", "0"),
        frontier_input_usd_per_million=number(prefix + "FRONTIER_INPUT_USD_PER_MILLION", "0"),
        frontier_output_usd_per_million=number(prefix + "FRONTIER_OUTPUT_USD_PER_MILLION", "0"),
        router_training_fingerprint=os.getenv(prefix + "ROUTER_TRAINING_FINGERPRINT", ""),
        laya_model=os.getenv("LAYA_MODEL", "typed-decisions"),
        laya_max_requests=integer("LAYA_MAX_REQUESTS", "100"),
        laya_max_input_units=integer("LAYA_MAX_INPUT_UNITS", "200000"),
        laya_device=os.getenv("LAYA_DEVICE", "mps"),
        laya_revision=os.getenv("LAYA_REVISION", "reviewed"),
        router_policy=os.getenv(prefix + "ROUTER_POLICY", "laya-choice"),
        router_seed=integer(prefix + "ROUTER_SEED", "17"),
        router_artifact=os.getenv(prefix + "ROUTER_ARTIFACT", ""),
        router_thresholds=os.getenv(prefix + "ROUTER_THRESHOLDS", ""),
        strands_url=os.getenv(prefix + "STRANDS_URL", ""),
        strands_model=os.getenv(prefix + "STRANDS_MODEL", ""),
        strands_checkpoint=os.getenv(prefix + "STRANDS_CHECKPOINT", ""),
        strands_device=os.getenv(prefix + "STRANDS_DEVICE", "mps"),
        execution_paid_enabled=os.getenv(prefix + "EXECUTION_PAID_ENABLED", "false").lower() == "true",
        execution_max_requests=integer(prefix + "EXECUTION_MAX_REQUESTS", "0"),
        execution_max_tokens=integer(prefix + "EXECUTION_MAX_TOKENS", "0"),
        execution_max_usd=number(prefix + "EXECUTION_MAX_USD", "0"),
        verification_threshold=optional_number(prefix + "VERIFICATION_THRESHOLD"),
        verification_threshold_source=os.getenv(prefix + "VERIFICATION_THRESHOLD_SOURCE", ""),
        cache_path=os.getenv(prefix + "CACHE_PATH", ""),
        cache_embedding_revision=os.getenv(prefix + "CACHE_EMBEDDING_REVISION", ""),
        cache_similarity_threshold=optional_number(prefix + "CACHE_SIMILARITY_THRESHOLD"),
        cache_similarity_threshold_source=os.getenv(prefix + "CACHE_SIMILARITY_THRESHOLD_SOURCE", ""),
        cache_verification_threshold=optional_number(prefix + "CACHE_VERIFICATION_THRESHOLD"),
        cache_verification_threshold_source=os.getenv(prefix + "CACHE_VERIFICATION_THRESHOLD_SOURCE", ""),
        cache_namespace=os.getenv(prefix + "CACHE_NAMESPACE", "local"),
        cache_ttl_seconds=integer(prefix + "CACHE_TTL_SECONDS", "86400"),
        cache_similarity_only_enabled=os.getenv(prefix + "CACHE_SIMILARITY_ONLY_ENABLED", "false").lower() == "true",
    )
