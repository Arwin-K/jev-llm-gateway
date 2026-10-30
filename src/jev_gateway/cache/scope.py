"""Exact cache reuse scope around a semantically variable final user message."""
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CacheScope:
    fingerprint: str
    namespace: str
    embedding_identity: str
    policy_identity: str
    model_identity: str
    generation_settings: str


@dataclass(frozen=True)
class CacheEntry:
    entry_id: str
    scope_fingerprint: str
    question: str
    answer: str
    created_at: str
    expires_at: str
    origin_tier: str
    origin_model: str
    acceptance: str
    verified: bool
    embedding_identity: str
    response: dict | None = None


def make_scope(messages: tuple[dict[str,str],...], *, namespace: str,
               embedding_identity: str, policy_identity: str, model_identity: str,
               max_output_tokens: int, temperature: float | None) -> CacheScope:
    if not messages or messages[-1]['role']!='user' or not namespace or not embedding_identity:
        raise ValueError('cache requires final user message, namespace, and embedding identity')
    instructions=[m for m in messages if m['role'] in {'system','developer'}]
    conversation=messages[:-1]
    generation={'max_output_tokens':max_output_tokens,'temperature':temperature}
    material={'namespace':namespace,'instructions':instructions,'conversation':conversation,
              'embedding_identity':embedding_identity,'policy_identity':policy_identity,
              'model_identity':model_identity,'generation':generation}
    fingerprint=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return CacheScope(fingerprint,namespace,embedding_identity,policy_identity,model_identity,
                      hashlib.sha256(json.dumps(generation,sort_keys=True).encode()).hexdigest())


def eligible(entry: CacheEntry, scope: CacheScope, *, now: datetime | None = None,
             allow_unverified: bool = False) -> bool:
    current=now or datetime.now(timezone.utc)
    try:
        expiry=datetime.fromisoformat(entry.expires_at)
    except ValueError:
        return False
    if expiry.tzinfo is None:
        return False
    return bool(entry.scope_fingerprint==scope.fingerprint and
                entry.embedding_identity==scope.embedding_identity and
                entry.acceptance=='accepted' and entry.answer and
                current<expiry and (entry.verified or allow_unverified))
