import pytest
from jev_gateway.evaluation.datasets import gsm8k, mmlu, mbpp


def test_gsm_final_marker_and_prompt():
    p = gsm8k({'question':'What is 1 + 1?', 'answer':'1+1=2\n#### 2'}, 7)
    assert p.reference == '2' and '####' not in p.prompt and p.source_id == '7'
    with pytest.raises(ValueError):
        gsm8k({'question':'x', 'answer':'2'}, 0)


def test_mmlu_order_and_no_answer_leak():
    p = mmlu({'question':'Pick one', 'choices':['red','blue','green','yellow'], 'answer':2, 'subject':'colors'}, 3)
    assert p.reference == 'C' and 'C. green' in p.prompt and 'answer index' not in p.prompt
    with pytest.raises(ValueError):
        mmlu({'question':'x','choices':['a','b'],'answer':1,'subject':'s'}, 0)


def test_mbpp_keeps_tests_private():
    p = mbpp({'task_id':11,'prompt':'Return 2','test_list':['assert f() == 2'],'code':'def f(): return 2'})
    assert 'assert' not in p.prompt and 'def f' not in p.prompt and len(p.tests) == 1
