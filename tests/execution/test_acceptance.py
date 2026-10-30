from jev_gateway.execution.acceptance import AcceptancePolicy
from jev_gateway.execution.verifier import VerificationDecision, EVENT, QUESTION_VERSION


def decision(probability):
    return VerificationDecision('r','hash',probability,EVENT,QUESTION_VERSION,'jev',1.,{})


def test_threshold_and_failure_modes_are_distinct():
    strict=AcceptancePolicy(.8,'validation-run-a')
    assert strict.assess(decision(.9)).outcome=='accepted_verified'
    assert strict.assess(decision(.7)).outcome=='rejected'
    assert strict.assess(None,error='timeout').outcome=='verification_failed'
    explicit=AcceptancePolicy(.8,'validation-run-a',on_failure='return_unverified')
    result=explicit.assess(None,error='timeout')
    assert result.outcome=='unverified_allowed' and not result.verified
