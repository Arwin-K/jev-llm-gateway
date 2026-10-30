from collections import Counter
from jev_gateway.cache.benchmark_data import load


def test_hand_authored_groups_preserve_near_miss_answer_changes():
    cases=load()
    assert len(cases)==12
    assert Counter(c.relation for c in cases)=={'paraphrase':4,'near_miss':4,'unrelated':4}
    assert all(c.split=='validation' for c in cases)
    assert all(c.seed_answer!=c.query_answer for c in cases if c.relation=='near_miss')
