from jev_gateway.evaluation.scoring import score_code


def test_code_scoring_outcomes_and_extraction():
    def execute(code, tests, imports, timeout):
        assert code == 'def f(): return 2'
        return {'status':'passed'}
    assert score_code('```python\ndef f(): return 2\n```', ['assert f() == 2'], executor=execute)['outcome'] == 'correct'
    for status, expected in [('failed_tests','incorrect'),('timeout','evaluator_error'),('environment_error','blocked'),('crashed','incorrect')]:
        assert score_code('def f(): return 2', [], executor=lambda *a, **k: {'status':status})['outcome'] == expected
    assert score_code('```python\nx=1', [], executor=execute)['outcome'] == 'parse_error'
