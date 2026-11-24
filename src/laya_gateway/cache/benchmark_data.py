"""Small versioned hand-authored validation cases for cache behavior."""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CacheCase:
    case_id: str
    group_id: str
    split: str
    relation: str
    seed_question: str
    seed_answer: str
    query: str
    query_answer: str
    provenance: str
    version: str


def load(path:Path=Path('data/cache_benchmark_v1.jsonl')) -> list[CacheCase]:
    cases=[CacheCase(**json.loads(line)) for line in path.read_text().splitlines() if line]
    if not cases or len({c.case_id for c in cases})!=len(cases):
        raise ValueError('nonempty unique case IDs required')
    groups={}
    for case in cases:
        if case.split!='validation' or case.relation not in {'paraphrase','near_miss','unrelated'} or \
           case.version!='cache-v1' or not case.provenance:
            raise ValueError('invalid development benchmark case')
        if case.relation=='paraphrase' and case.seed_answer!=case.query_answer or \
           case.relation=='near_miss' and case.seed_answer==case.query_answer:
            raise ValueError('relation contradicts answer key')
        seed=(case.seed_question,case.seed_answer)
        if case.group_id in groups and groups[case.group_id]!=seed:
            raise ValueError('related cases must share seed and group')
        groups[case.group_id]=seed
    return cases
