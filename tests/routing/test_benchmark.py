import asyncio
from jev_gateway.config import from_env
from jev_gateway.routing.admission import request_for
from jev_gateway.routing.baselines import FixedRouter
from jev_gateway.routing.benchmark import measure


def test_decision_only_measurement_records_denominator():
    settings=from_env()
    requests=[request_for(settings, ({'role':'user','content':'x'},),32,str(i)) for i in range(3)]
    report=asyncio.run(measure(FixedRouter('small'),requests,warmup=1))
    assert report['attempted']==2 and report['successful']==2
    assert report['p95_ms'] is not None and report['errors']==[]
