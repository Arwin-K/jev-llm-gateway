from jev_gateway.day6.workload import make


def test_synthetic_workload_is_repeatable_and_has_defined_lengths():
    left = make(23, 8)
    assert left == make(23, 8)
    assert [p['target_input_words'] for p in left['prompts']] == [32, 64, 128, 256] * 2
    assert len({p['prompt'] for p in left['prompts']}) == 8
