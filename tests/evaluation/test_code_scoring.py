from laya_gateway.evaluation.scoring import score_code


def test_code_scoring_outcomes_and_extraction():
    def execute(code, tests, imports, timeout):
        assert code == 'def f(): return 2'
        return {'status':'passed'}
    assert score_code('```python\ndef f(): return 2\n```', ['assert f() == 2'], executor=execute)['outcome'] == 'correct'
    for status, expected in [('failed_tests','incorrect'),('timeout','evaluator_error'),('environment_error','blocked'),('crashed','incorrect')]:
        assert score_code('def f(): return 2', [], executor=lambda *a, **k: {'status':status})['outcome'] == expected
    assert score_code('```python\nx=1', [], executor=execute)['outcome'] == 'parse_error'


def test_single_fence_with_explanation_is_scored_but_not_format_compliant():
    from laya_gateway.evaluation.scoring import format_compliant
    seen = []
    def execute(code, tests, imports, timeout):
        seen.append(code); return {'status':'passed'}
    raw = 'Here is the function:\n\n```python\ndef f(): return 2\n```\n\nIt returns 2.'
    assert score_code(raw, ['assert f() == 2'], executor=execute)['outcome'] == 'correct' and seen == ['def f(): return 2']
    two = '```python\ndef f(): return 2\n```\n\n```python\nprint(f())\n```'
    assert score_code(two, [], executor=execute)['error_category'] == 'ambiguous_code'
    assert format_compliant('code', raw, None) is False
    assert format_compliant('code', '```python\ndef f(): return 2\n```', None) is True
    assert format_compliant('code', 'def f(): return 2', None) is True
