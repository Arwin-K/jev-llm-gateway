import pytest
from jev_gateway.routing import Decision, RoutingRequest
from jev_gateway.routing.contracts import RoutingError, require_eligible


def request():
    return RoutingRequest(({'role': 'user', 'content': 'hello'},), 32, 'a', 'settings-a', ('small',))


def test_decision_carries_identity_and_defined_event():
    selected = Decision('small', 'fixed', '1', 0.1, request_id='a', settings_fingerprint='settings-a',
                        probability_event='oracle tier label', probabilities={'small': .9})
    assert require_eligible(selected, request()) == selected
    with pytest.raises(RoutingError):
        require_eligible(Decision('medium', 'fixed', '1', 0), request())


def test_invalid_decision_rejected():
    with pytest.raises(ValueError):
        Decision('large', 'fixed', '1', 0)
    with pytest.raises(ValueError):
        Decision('small', 'fixed', '1', 0, probabilities={'small': .5})
