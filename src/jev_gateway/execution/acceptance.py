"""Explicit verifier acceptance and failure policy."""
from dataclasses import dataclass
from math import isfinite

from .verifier import VerificationDecision


@dataclass(frozen=True)
class Assessment:
    outcome: str
    reason: str
    probability: float | None
    threshold: float
    threshold_source: str
    verified: bool


@dataclass(frozen=True)
class AcceptancePolicy:
    threshold: float
    threshold_source: str
    on_failure: str = 'fail_closed'

    def __post_init__(self):
        if not isfinite(self.threshold) or not 0 <= self.threshold <= 1 or not self.threshold_source:
            raise ValueError('finite threshold and source identity required')
        if self.on_failure not in {'fail_closed','return_unverified'}:
            raise ValueError('unknown verification failure mode')

    def assess(self, decision: VerificationDecision | None, *, error: str | None = None) -> Assessment:
        if error or decision is None:
            if self.on_failure == 'return_unverified':
                return Assessment('unverified_allowed', error or 'no_decision', None,
                                  self.threshold, self.threshold_source, False)
            return Assessment('verification_failed', error or 'no_decision', None,
                              self.threshold, self.threshold_source, False)
        if not isfinite(decision.probability) or not 0 <= decision.probability <= 1:
            return self.assess(None, error='invalid_probability')
        accepted = decision.probability >= self.threshold
        return Assessment('accepted_verified' if accepted else 'rejected',
                          'threshold_met' if accepted else 'below_threshold',
                          decision.probability, self.threshold, self.threshold_source, accepted)
