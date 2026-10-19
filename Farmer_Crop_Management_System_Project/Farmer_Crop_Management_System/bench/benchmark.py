"""Simple benchmark script to measure average response time for the dashboard and reports endpoints.

Requires `requests` library. Run locally against your dev server:

    pip install requests
    python bench/benchmark.py http://127.0.0.1:5000  --runs 20

It measures mean, min, max and prints per-endpoint results.
"""

import sys
import time
import argparse

try:
    import requests
except Exception:
    print('requests library is required: pip install requests')
    raise


def measure(url, path, runs=10):
    times = []
    full = url.rstrip('/') + path
    for i in range(runs):
        t0 = time.perf_counter()
        r = requests.get(full, allow_redirects=True)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)
        if r.status_code >= 400:
            print(f'Warning: {full} returned status {r.status_code} on run {i+1}')
    return times


def summarize(times):
    return {'runs': len(times), 'mean_ms': sum(times)/len(times) if times else 0,
            'min_ms': min(times) if times else 0, 'max_ms': max(times) if times else 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base_url', help='Base URL of the running app, e.g. http://127.0.0.1:5000')
    parser.add_argument('--runs', type=int, default=10)
    args = parser.parse_args()

    endpoints = ['/dashboard', '/reports']
    for ep in endpoints:
        print(f'Measuring {ep} for {args.runs} runs...')
        times = measure(args.base_url, ep, runs=args.runs)
        print(summarize(times))
