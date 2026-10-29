"""Shared, auditable router input and output contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

TIERS = ('small', 'medium', 'frontier')


class RoutingError(RuntimeError):
    """A policy could not make an admissible decision."""


@dataclass(frozen=True)
class RoutingRequest:
    messages: tuple[dict[str, str], ...]
    max_output_tokens: int
    request_id: str
    settings_fingerprint: str
    eligible_tiers: tuple[str, ...]

    def __post_init__(self):
        if not self.messages or not self.request_id or not self.settings_fingerprint:
            raise ValueError('routing input needs messages and identities')
        if self.max_output_tokens < 1 or not set(self.eligible_tiers).issubset(TIERS):
            raise ValueError('invalid routing limits or eligible tiers')

    @property
    def text(self) -> str:
        return '\n'.join(f'{message["role"]}: {message["content"]}' for message in self.messages)


@dataclass(frozen=True)
class Decision:
    tier: str | None
    policy: str
    version: str
    duration_ms: float
    outcome: str = 'selected'
    fallback_reason: str | None = None
    request_id: str = ''
    settings_fingerprint: str = ''
    probability_event: str | None = None
    probabilities: Mapping[str, float] = field(default_factory=dict)
    usage: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.tier is not None and self.tier not in TIERS:
            raise ValueError('unknown selected tier')
        if not self.policy or not self.version or self.duration_ms < 0:
            raise ValueError('invalid decision metadata')
        if self.outcome == 'selected' and self.tier is None:
            raise ValueError('selected decision needs a tier')
        if self.probabilities and not self.probability_event:
            raise ValueError('probability event must be defined')
        if any(not 0 <= value <= 1 for value in self.probabilities.values()):
            raise ValueError('probability outside [0,1]')


class Router(Protocol):
    name: str
    version: str

    async def decide(self, request: RoutingRequest) -> Decision: ...


def require_eligible(decision: Decision, request: RoutingRequest) -> Decision:
    if decision.tier is None or decision.tier not in request.eligible_tiers:
        raise RoutingError('selected tier is ineligible')
    return decision
