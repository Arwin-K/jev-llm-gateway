import pytest
from jev_gateway.config import from_env
from jev_gateway.evaluation.serving import Workload, run


def test_workload_validation_and_paid_gate():
    with pytest.raises(ValueError): Workload('small','x',0,0,1,10,0,'off','mac','warm')
    workload=Workload('frontier','x',1,0,1,10,0,'off','api','unverified')
    with pytest.raises(PermissionError):
        import asyncio
        asyncio.run(run(workload,from_env(),None))
