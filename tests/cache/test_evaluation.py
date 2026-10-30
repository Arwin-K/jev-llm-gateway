from jev_gateway.cache.benchmark_data import load
from jev_gateway.cache.evaluation import CacheObservation, report


def test_harmful_reuse_denominators_and_fixture_origin():
    cases=load()
    near=next(c for c in cases if c.relation=='near_miss')
    observation=CacheObservation(near.case_id,'similarity_only','fixture','fixture-a','seed-a',
        'fake@rev',0,False,True,True,None,False,near.seed_answer,None,(None,),(None,))
    rows=report(cases,[observation])
    row=next(r for r in rows if r['mode']=='similarity_only' and r['execution']=='fixture')
    assert row['harmful_reuse']==1 and row['harmful_among_reused']==1
    assert row['harmful_per_all_queries']==1/len(cases)
    assert row['end_to_end_p50_ms'] is None and row['total_charge_usd'] is None
