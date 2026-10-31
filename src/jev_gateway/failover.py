"""Conservative local availability failover for buffered automatic generation."""
import httpx


def availability_failure(exc):
    return (isinstance(exc, httpx.RequestError) or
            isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500)


def alternate_tier(original, eligible):
    # Never add a paid provider as an implicit alternate.
    for tier in ("medium", "small") if original == "small" else ("small", "medium"):
        if tier != original and tier in eligible:
            return tier
    return None
