"""Client-observed serving metrics; no inferred token counts."""
import math


def percentile(values, q):
    if not values: return None
    ordered=sorted(values)
    return ordered[max(0,math.ceil(q*len(ordered))-1)]


def serving_report(run):
    rows=[r for r in run['observations'] if not r['warmup']]
    ok=[r for r in rows if r['status']=='ok']
    failed=[r for r in rows if r['status']!='ok']
    latencies=[r['latency_s'] for r in ok]
    all_latency=[r['latency_s'] for r in rows if r.get('latency_s') is not None]
    first=[r['first_visible_s'] for r in ok if r.get('first_visible_s') is not None]
    tpot=[(r['latency_s']-r['first_visible_s'])/(r['completion_tokens']-1) for r in ok if isinstance(r.get('completion_tokens'),int) and r['completion_tokens']>=2 and r.get('first_visible_s') is not None and r['latency_s']>=r['first_visible_s']]
    elapsed=run['elapsed_s']
    return {'requests':len(rows),'completed':len(ok),'errors':len(failed),'error_rate':len(failed)/len(rows) if rows else None,'client_latency_success_p50_s':percentile(latencies,.5),'client_latency_success_p95_s':percentile(latencies,.95),'client_latency_all_observed_p95_s':percentile(all_latency,.95),'first_visible_p50_s':percentile(first,.5),'first_visible_p95_s':percentile(first,.95),'first_visible_count':len(first),'tpot_proxy_p50_s':percentile(tpot,.5),'tpot_proxy_count':len(tpot),'completed_requests_per_s':len(ok)/elapsed if elapsed>0 else None,'intended_arrivals':len(rows),'achieved_starts':sum(r.get('achieved_start_offset_s') is not None for r in rows)}
