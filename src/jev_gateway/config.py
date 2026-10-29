"""Typed, explicit runtime configuration. Secrets are read only from environment."""

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
    frontier_max_requests: int = 0
    frontier_max_tokens: int = 0
    frontier_max_usd: float = 0.0
    frontier_input_usd_per_million: float = 0.0
    frontier_output_usd_per_million: float = 0.0
    router_training_fingerprint: str = ""

    def __post_init__(self):
        if not 0 < self.timeout_seconds <= 300:
            raise ConfigError("timeout_seconds must be between 0 and 300")
        if not 1 <= self.max_output_tokens <= 8192:
            raise ConfigError("max_output_tokens must be between 1 and 8192")
        if min(self.frontier_max_requests, self.frontier_max_tokens) < 0 or self.frontier_max_usd < 0:
            raise ConfigError("frontier limits cannot be negative")

    @property
    def frontier_enabled(self):
        return bool(self.frontier.model != "UNCONFIGURED" and self.frontier.api_key and self.frontier_max_requests > 0 and
                    self.frontier_max_tokens > 0 and self.frontier_max_usd > 0 and
                    self.frontier_input_usd_per_million > 0 and self.frontier_output_usd_per_million > 0)

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

    return Settings(
        small=Backend("small", os.getenv("JEV_SMALL_MODEL", "qwen2.5:1.5b"), os.getenv("JEV_SMALL_URL", "http://127.0.0.1:11434/v1"), max_context_tokens=integer("JEV_SMALL_CONTEXT_TOKENS", "4096")),
        medium=Backend("medium", os.getenv("JEV_MEDIUM_MODEL", "qwen2.5:7b"), os.getenv("JEV_MEDIUM_URL", "http://127.0.0.1:11434/v1"), max_context_tokens=integer("JEV_MEDIUM_CONTEXT_TOKENS", "4096")),
        frontier=Backend("frontier", os.getenv("JEV_FRONTIER_MODEL") or "UNCONFIGURED", os.getenv("JEV_FRONTIER_URL", "https://api.openai.com/v1"), "JEV_FRONTIER_API_KEY", max_context_tokens=integer("JEV_FRONTIER_CONTEXT_TOKENS", "4096")),
        timeout_seconds=number("JEV_TIMEOUT_SECONDS", "60"),
        max_output_tokens=integer("JEV_MAX_OUTPUT_TOKENS", "256"),
        frontier_max_requests=integer("JEV_FRONTIER_MAX_REQUESTS", "0"),
        frontier_max_tokens=integer("JEV_FRONTIER_MAX_TOKENS", "0"),
        frontier_max_usd=number("JEV_FRONTIER_MAX_USD", "0"),
        frontier_input_usd_per_million=number("JEV_FRONTIER_INPUT_USD_PER_MILLION", "0"),
        frontier_output_usd_per_million=number("JEV_FRONTIER_OUTPUT_USD_PER_MILLION", "0"),
        router_training_fingerprint=os.getenv("JEV_ROUTER_TRAINING_FINGERPRINT", ""),
    )
