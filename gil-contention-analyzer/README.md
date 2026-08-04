# gil-contention-analyzer

## Why this exists
Python's GIL remains a major source of hidden latency in multithreaded services. Existing profilers report CPU time but rarely quantify how long threads actually waited for the GIL. gil-contention-analyzer attaches lightweight hooks to measure per-thread GIL acquisition latency, produces publication-quality histograms, and suggests concrete fixes (number of workers, task granularity, or migration to asyncio).

## Features
- Zero-code-change measurement via import hook or explicit context manager
- Per-thread and aggregate histograms (p50/p95/p99)
- Automatic detection of contention hotspots with source location
- Export to JSON, SVG, or terminal braille charts
- Recommendations engine based on observed wait distribution
- Works with threading, concurrent.futures, and uvicorn/gunicorn workers

## Installation
```bash
pip install gil-contention-analyzer
```

## Usage
```bash
python -m gil_contention_analyzer --threads 8 --duration 30s my_app.py
```

## Architecture
Uses sys.setprofile with minimal overhead (<3% in steady state) and a lock-free ring buffer. Post-processing builds HDR histograms and renders via rich.

## Alternatives considered
cProfile, py-spy, and austin do not expose GIL wait times. vmprof requires custom builds. This tool focuses exclusively on GIL contention with production-grade ergonomics.