from jev_gateway.evaluation.latency import serving_report, percentile


def test_latency_denominators_and_token_guard():
    rows=[{'warmup':True,'status':'ok','latency_s':99,'first_visible_s':1,'completion_tokens':2}, {'warmup':False,'status':'ok','latency_s':2,'first_visible_s':.5,'completion_tokens':1,'achieved_start_offset_s':0},{'warmup':False,'status':'ok','latency_s':4,'first_visible_s':1,'completion_tokens':4,'achieved_start_offset_s':1},{'warmup':False,'status':'error','latency_s':5,'first_visible_s':None,'completion_tokens':None,'achieved_start_offset_s':2}]
    report=serving_report({'observations':rows,'elapsed_s':10})
    assert report['requests']==3 and report['errors']==1 and report['completed_requests_per_s']==.2
    assert report['client_latency_success_p95_s']==4 and report['client_latency_all_observed_p95_s']==5
    assert report['tpot_proxy_count']==1 and report['tpot_proxy_p50_s']==1
    assert percentile([], .95) is None
