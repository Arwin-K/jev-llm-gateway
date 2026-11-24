from laya_gateway.evaluation.scoring import format_compliant, score_choice, score_choice_strict


def test_choice_conservative_extraction():
    assert score_choice('B', 'B')['outcome'] == 'correct'
    assert score_choice('The answer is C.', 'B')['outcome'] == 'incorrect'
    assert score_choice('Reasoning\nAnswer: A', 'A')['outcome'] == 'correct'
    assert score_choice('A or B', 'A')['outcome'] == 'parse_error'
    assert score_choice('The cat is happy', 'A')['outcome'] == 'parse_error'
    assert score_choice('Answer: A\nAnswer: B', 'A')['error_category'] == 'ambiguous'
    assert score_choice('Answer: A', 'A', truncated=True)['error_category'] == 'truncated'


def test_choice_accepts_decorated_final_line():
    assert score_choice('Reasoning\nAnswer: B. Paris', 'B')['outcome'] == 'correct'
    assert score_choice('**Answer: C**', 'C')['outcome'] == 'correct'
    assert score_choice('Answer: (D)', 'D')['outcome'] == 'correct'
    assert score_choice('Answer: C) A plant cell', 'C')['outcome'] == 'correct'


def test_choice_rejects_lists_and_lowercase_words():
    assert score_choice('Answer: A, B, C, or D', 'A')['error_category'] == 'ambiguous'
    assert score_choice('Answer: A or B', 'A')['outcome'] == 'parse_error'
    assert score_choice('Answer: a plant cell', 'A')['outcome'] == 'parse_error'
    assert score_choice('Answer: About', 'A')['outcome'] == 'parse_error'


def test_strict_choice_and_compliance():
    assert score_choice_strict('Answer: B. Paris', 'B')['outcome'] == 'parse_error'
    assert format_compliant('choice', 'Answer: B', 'B') is True
    assert format_compliant('choice', '**Answer: B**', 'B') is False
