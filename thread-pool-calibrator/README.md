# thread-pool-calibrator

## Why this exists
Choosing thread pool sizes is notoriously difficult. Too few threads under-utilize hardware; too many cause context-switch thrashing, memory bloat, and unpredictable tail latencies. This tool replaces guesswork with simulation-driven calibration.

## Features
- Discrete-event simulator for I/O-bound, CPU-bound, and mixed workloads
- Live attachment to running Python processes via sampling profiler
- Statistical output: p50/p95/p99 latency, throughput, and contention heatmaps
- Automatic recommendation engine with confidence intervals
- Exportable reports (JSON, Markdown, SVG)

## Installation
pip install thread-pool-calibrator

## Usage
thread-pool-calibrator calibrate --workload examples/mixed.yaml --target-p95 120ms

## Architecture
See docs/architecture.md