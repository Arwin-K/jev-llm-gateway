from jev_gateway.evaluation.scoring import score_math


def test_math_formats_and_ambiguity():
    assert score_math('Work\nAnswer: -1,200.5', '-1200.5')['outcome'] == 'correct'
    assert score_math('Answer: 1/2', '0.5')['outcome'] == 'correct'
    assert score_math('Answer: 3', '2')['outcome'] == 'incorrect'
    assert score_math('Answer: 2\nAnswer: 3', '2')['outcome'] == 'parse_error'
    assert score_math('Maybe two or three', '2')['outcome'] == 'parse_error'
    assert score_math('Answer: 2 kg', '2')['outcome'] == 'parse_error'
