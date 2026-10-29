import pytest
from jev_gateway.routing.tuning import ValidationCase, select


def case(split='validation'):
    return ValidationCase('p',split,{'small':.7,'medium':.9},
                          {'small':'incorrect','medium':'correct'},
                          {'small':.01,'medium':.02},.001)


def test_validation_selects_lowest_feasible_observed_cost():
    report=select([case()], [{'small':.5,'medium':.5,'frontier':.5},
                              {'small':.8,'medium':.8,'frontier':.8}],
                  min_correct_completion_rate=1)
    assert report['selected']['thresholds']['small']==.8
    assert report['selected']['total_charge_usd']==pytest.approx(.021)
    assert report['selected']['execution']=='offline_replay'


def test_test_split_and_unknown_cost_cannot_select():
    with pytest.raises(PermissionError):
        select([case('test')],[],min_correct_completion_rate=0)
    sample=case()
    unknown=ValidationCase(sample.prompt_id,sample.split,sample.probabilities,
                           sample.outcomes,sample.charges_usd,None)
    assert select([unknown],[{'small':.8,'medium':.8,'frontier':.8}],
                  min_correct_completion_rate=0)['selected'] is None
