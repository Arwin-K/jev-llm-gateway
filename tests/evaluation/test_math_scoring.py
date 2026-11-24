from laya_gateway.evaluation.scoring import format_compliant, score_math, score_math_strict


def test_strict_v1_formats_and_ambiguity():
    assert score_math_strict('Work\nAnswer: -1,200.5', '-1200.5')['outcome'] == 'correct'
    assert score_math_strict('Answer: 1/2', '0.5')['outcome'] == 'correct'
    assert score_math_strict('Answer: 3', '2')['outcome'] == 'incorrect'
    assert score_math_strict('Answer: 2\nAnswer: 3', '2')['outcome'] == 'parse_error'
    assert score_math_strict('Maybe two or three', '2')['outcome'] == 'parse_error'
    assert score_math_strict('Answer: 2 kg', '2')['outcome'] == 'parse_error'


def test_final_answer_accepts_units_currency_inline_and_boxed():
    # Real qwen2.5 final lines from evidence/day7/answer-format-probe-20261113.txt.
    assert score_math('Answer: 60 marbles', '60')['outcome'] == 'correct'
    assert score_math('Answer: $2,000', '2000')['outcome'] == 'correct'
    assert score_math('Therefore, the sum of the ages is Answer: 71.', '71')['outcome'] == 'correct'
    assert score_math('so the length is \\(\\boxed{632}\\) cm.', '632')['outcome'] == 'correct'
    assert score_math('\\[ \\boxed{110.00} \\]', '110')['outcome'] == 'correct'
    assert score_math('**Answer: 18**', '18')['outcome'] == 'correct'
    assert score_math('Answer: \\boxed{5}', '5')['outcome'] == 'correct'
    assert score_math('Work\nAnswer: -1,200.5', '-1200.5')['outcome'] == 'correct'
    assert score_math('Answer: 3', '2')['outcome'] == 'incorrect'


def test_final_answer_still_refuses_to_guess():
    assert score_math('Answer: 2\nAnswer: 3', '2')['error_category'] == 'conflicting'
    assert score_math('Answer: 2\n\\boxed{3}', '2')['outcome'] == 'parse_error'
    assert score_math('Answer: 3 + 4 = 7', '7')['outcome'] == 'parse_error'
    assert score_math('Answer: <number>', '5')['outcome'] == 'parse_error'
    assert score_math('Therefore, the answer is 6.', '6')['outcome'] == 'parse_error'
    assert score_math('Maybe two or three', '2')['outcome'] == 'parse_error'
    assert score_math('Answer: 2', 'not a number')['outcome'] == 'evaluator_error'


def test_format_compliance_uses_strict_reader():
    assert format_compliant('math', 'Answer: 60', '60') is True
    assert format_compliant('math', 'Answer: 60 marbles', '60') is False
    assert format_compliant('other', 'x', None) is None
    assert format_compliant('math', None, '1') is None
