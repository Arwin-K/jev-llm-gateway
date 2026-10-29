from types import SimpleNamespace
import pytest
from jev_gateway.evaluation.oracle import label


def test_oracle_missing_failed_tie_and_none():
    p=SimpleNamespace(prompt_id='p',split='train')
    def r(t,o,c): return SimpleNamespace(prompt_id='p',tier=t,outcome=o,charge_usd=c)
    rows=[r('small','correct',.1),r('medium','correct',.1),r('frontier','incorrect',.3)]
    x=label(p,rows); assert x.status=='labeled' and x.tier=='small' and x.tied_tiers==('small','medium')
    assert label(p,rows[:2]).status=='incomplete'
    assert label(p,[rows[0],r('medium','backend_error',.1),rows[2]]).status=='failed_evaluation'
    assert label(p,[r('small','incorrect',.1),r('medium','incorrect',.2),r('frontier','parse_error',.3)]).status=='none_correct'
    assert label(p,[rows[0],r('medium','incorrect',None),rows[2]]).status=='incomparable_cost'
    with pytest.raises(PermissionError): label(SimpleNamespace(prompt_id='p',split='validation'),rows)
