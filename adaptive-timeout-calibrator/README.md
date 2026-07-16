# adaptive-timeout-calibrator

## Why this exists
Hard-coded timeouts are a leading cause of cascading failures. This tool ingests latency histograms (from logs, Prometheus, or HAR), fits a latency model, and emits production-ready adaptive timeout values together with SLO compliance proofs.

## Features
- Multiple distribution fitting (log-normal, gamma, Weibull)
- Error budget and burn-rate aware recommendations
- Percentile and tail-latency targeting
- Export to YAML, JSON, and Kubernetes annotations
- Historical drift detection between runs

## Installation
```bash
pip install adaptive-timeout-calibrator
```

## Usage
```bash
adaptive-timeout-calibrator histogram.json --slo 0.999 --budget 0.01 --output timeout.yaml
```

## Architecture
Pure Python, zero external services. Uses scipy for fitting and rich for CLI output.

## Benchmarks
Fits a 100k sample histogram in <120 ms on a 2023 MacBook Pro.

## Alternatives considered
- Manual p99 + 2×; too brittle
- circuit-breaker-simulator; focuses on state machine, not timeout math