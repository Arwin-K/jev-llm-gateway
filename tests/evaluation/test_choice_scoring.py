from jev_gateway.evaluation.scoring import score_choice


def test_choice_conservative_extraction():
    assert score_choice('B', 'B')['outcome'] == 'correct'
    assert score_choice('The answer is C.', 'B')['outcome'] == 'incorrect'
    assert score_choice('Reasoning\nAnswer: A', 'A')['outcome'] == 'correct'
    assert score_choice('A or B', 'A')['outcome'] == 'parse_error'
    assert score_choice('The cat is happy', 'A')['outcome'] == 'parse_error'
    assert score_choice('Answer: A\nAnswer: B', 'A')['error_category'] == 'ambiguous'
    assert score_choice('Answer: A', 'A', truncated=True)['error_category'] == 'truncated'
