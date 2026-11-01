"""Bounded, client-side OpenAI-compatible serving benchmark."""

import argparse
import asyncio
import statistics
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .common import digest, read_json, write_new


async def run(workload: Path, config: Path, *, endpoint: str, concurrency: int,
              interval: float, warmup: int, timeout: float, label: str) -> dict:
    if concurrency < 1 or warmup < 0 or interval < 0 or timeout <= 0:
        raise ValueError('invalid benchmark limits')
    if not endpoint.startswith('http://127.0.0.1:') and not endpoint.startswith('http://localhost:'):
        raise ValueError('benchmark endpoint must be loopback')
    cases, settings = read_json(workload), read_json(config)
    if cases.get('origin') != 'synthetic' or not cases.get('prompts'):
        raise ValueError('expected nonempty synthetic workload')
    if 'REPLACE_' in str(settings) or settings.get('max_output_tokens', 0) <= 0:
        raise ValueError('resolve serving identity and output cap before running')
    semaphore = asyncio.Semaphore(concurrency)
    records = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        async def request(case, phase):
            async with semaphore:
                started = time.perf_counter()
                try:
                    response = await client.post(endpoint.rstrip('/') + '/v1/chat/completions', json={
                        'model': settings['model'], 'messages': [{'role': 'user', 'content': case['prompt']}],
                        'max_tokens': settings['max_output_tokens'], 'temperature': 0,
                    })
                    response.raise_for_status()
                    data = response.json()
                    answer = data['choices'][0]['message']['content'] or ''
                    usage = data.get('usage') or {}
                    outcome = {'status': 'ok', 'http_status': response.status_code,
                               'output_words': len(answer.split()),
                               'completion_tokens': usage.get('completion_tokens'),
                               'finish_reason': data['choices'][0].get('finish_reason')}
                except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
                    outcome = {'status': 'error', 'error_type': type(exc).__name__}
                records.append({'id': case['id'], 'phase': phase,
                                'latency_ms': (time.perf_counter() - started) * 1000, **outcome})
        for case in cases['prompts'][:warmup]:
            await request(case, 'warmup')
        start = time.perf_counter()
        tasks = []
        for case in cases['prompts']:
            tasks.append(asyncio.create_task(request(case, 'measured')))
            if interval:
                await asyncio.sleep(interval)
        await asyncio.gather(*tasks)
        duration = time.perf_counter() - start
    measured = [r for r in records if r['phase'] == 'measured']
    ok = sorted(r['latency_ms'] for r in measured if r['status'] == 'ok')
    percentile = lambda fraction: ok[min(len(ok)-1, int((len(ok)-1)*fraction))] if ok else None
    return {'schema': 'jev.day6.benchmark.v1', 'run_id': uuid.uuid4().hex,
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
            'label': label, 'origin': 'live_client' if ok else 'live_client_no_success',
            'workload_sha256': digest(workload), 'config_sha256': digest(config),
            'endpoint': endpoint, 'client_host': __import__('platform').node(),
            'arrival': 'fixed_interval' if interval else 'burst', 'interval_seconds': interval,
            'concurrency_cap': concurrency, 'warmup_requests': warmup, 'timeout_seconds': timeout,
            'duration_seconds': duration, 'request_count': len(measured), 'success_count': len(ok),
            'error_count': len(measured)-len(ok), 'throughput_success_per_second': len(ok)/duration,
            'latency_ms': {'p50': percentile(.5), 'p95': percentile(.95), 'mean': statistics.mean(ok) if ok else None},
            'records': records}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--workload', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8000')
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--interval', type=float, default=0)
    parser.add_argument('--warmup', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--label', required=True)
    args = parser.parse_args(argv)
    result = asyncio.run(run(args.workload, args.config, endpoint=args.endpoint,
                             concurrency=args.concurrency, interval=args.interval,
                             warmup=args.warmup, timeout=args.timeout, label=args.label))
    write_new(args.output, result)


if __name__ == '__main__':
    main()
