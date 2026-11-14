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


def test_v2_templates_put_format_last_and_name_the_function():
    from jev_gateway.evaluation.datasets import TEMPLATES_BY_VERSION, fingerprint, required_function
    math = gsm8k({'question':'What is 1 + 1?', 'answer':'#### 2'}, 7)
    assert math.prompt.endswith('Answer: <number>') and math.template_fingerprint == fingerprint(TEMPLATES_BY_VERSION['v2']['math'])
    choice = mmlu({'question':'Pick one', 'choices':['red','blue','green','yellow'], 'answer':2, 'subject':'colors'}, 3)
    assert choice.prompt.endswith('Answer: <letter>') and 'D. yellow' in choice.prompt
    code = mbpp({'task_id':11,'prompt':'Return 2','test_list':['assert set(f_two()) == {2}', 'assert math.isclose(f_two(), 2)']})
    assert 'named `f_two`' in code.prompt and 'assert' not in code.prompt
    assert required_function(['assert f(1) == g(2)']) is None
    assert required_function(['assert True']) is None
    unnamed = mbpp({'task_id':12,'prompt':'Do it','test_list':['assert True']})
    assert unnamed.prompt.startswith('Write Python code for this task. Return code only.')


def test_v1_templates_remain_reproducible():
    from jev_gateway.evaluation.datasets import TEMPLATES_BY_VERSION, fingerprint
    p = gsm8k({'question':'Q?', 'answer':'#### 2'}, 0, version='v1')
    assert p.prompt == 'Solve the problem. End with Answer: <number>.\n\nQ?'
    assert p.template_fingerprint == fingerprint(TEMPLATES_BY_VERSION['v1']['math'])
    assert mbpp({'task_id':1,'prompt':'Do','test_list':['assert f()']}, version='v1').prompt == 'Write Python code for this task. Return code only.\n\nDo'
