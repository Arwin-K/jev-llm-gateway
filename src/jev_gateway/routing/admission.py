"""Conservative pre-decision eligibility from configured capacity and spend gates."""
import hashlib
import json

from jev_gateway.config import Settings
from .contracts import RoutingRequest, TIERS


def fingerprint(settings: Settings) -> str:
    # No credentials enter this identity.
    public = [(t, settings.backend(t).model, settings.backend(t).base_url,
               settings.backend(t).max_context_tokens) for t in TIERS]
    return hashlib.sha256(json.dumps(public, separators=(',', ':')).encode()).hexdigest()


def estimate_input_tokens(messages: tuple[dict[str, str], ...]) -> int:
    # Deliberately conservative for ordinary UTF-8 text; actual tokenizer must be checked at execution.
    return sum(len(m['content'].encode('utf-8')) + 8 for m in messages)


def eligible_tiers(settings: Settings, messages: tuple[dict[str, str], ...], output_tokens: int) -> tuple[str, ...]:
    estimated = estimate_input_tokens(messages) + output_tokens
    return tuple(t for t in TIERS if (t != 'frontier' or settings.frontier_enabled) and
                 settings.backend(t).max_context_tokens >= estimated)


def request_for(settings: Settings, messages: tuple[dict[str, str], ...], output_tokens: int,
                request_id: str) -> RoutingRequest:
    return RoutingRequest(messages, output_tokens, request_id, fingerprint(settings),
                          eligible_tiers(settings, messages, output_tokens))
