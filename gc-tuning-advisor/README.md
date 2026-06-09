# gc-tuning-advisor

## Why this exists
Production Python services often suffer from unpredictable latency spikes or excessive CPU usage due to suboptimal GC settings. Tuning `gc.set_threshold` and related parameters requires deep understanding of allocation patterns. gc-tuning-advisor parses verbose GC logs, builds a statistical model of generation behavior, and produces concrete, workload-specific recommendations.

## Features
- Parses CPython GC logs from 3.8+
- Computes allocation rates, promotion rates, and pause distributions
- Recommends threshold tuples with expected impact
- Supports both CLI and library usage
- Exports Prometheus-compatible metrics

## Installation
```bash
pip install gc-tuning-advisor
```

## Usage
```bash
python -m gc_tuning_advisor analyze gc.log --format table
```

## Architecture
See docs/architecture.md

## Benchmarks
On a 2M-line production log the tool completes in <800ms with <60MB RSS.

## Alternatives considered
- Manual tuning via `gc` module
- py-spy / memray (complementary, not replacement)
- JVM-style GC log analyzers (different semantics)