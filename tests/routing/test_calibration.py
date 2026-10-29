import pytest
from jev_gateway.routing.calibration import BinaryObservation, binary_report, oracle_label_report, write_reliability_svg


def test_binary_calibration_and_coverage(tmp_path):
    event='named generator externally scores correct'
    report=binary_report([BinaryObservation(.8,True,event),BinaryObservation(.2,False,event)],bins=2,expected=3)
    assert report['brier']==pytest.approx(.04)
    assert report['ece']==pytest.approx(.2)
    assert report['missing']==1
    write_reliability_svg(report,tmp_path/'reliability.svg')
    assert '<svg' in (tmp_path/'reliability.svg').read_text()


def test_oracle_multiclass_event_is_separate():
    report=oracle_label_report([({'small':.8,'medium':.1,'frontier':.1},'small')],expected=2)
    assert report['multiclass_brier']==pytest.approx(.06)
    assert report['missing']==1
    with pytest.raises(ValueError):
        binary_report([BinaryObservation(.8,True,'a'), BinaryObservation(.7,False,'b')])
