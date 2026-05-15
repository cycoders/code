# metrics-cardinality-cli

## Why this exists
High-cardinality metrics are the #1 cause of Prometheus/VictoriaMetrics performance degradation and OOMs in production. Engineers need a fast, local tool to audit /metrics endpoints before deploying new instrumentation.

## Features
- Parses exposition format in a single pass
- Ranks metrics by estimated series count using label cardinality heuristics
- Supports histogram and summary quantile expansion
- Configurable cardinality thresholds and ignore patterns
- Beautiful table + JSON output with suggested fixes
- Streaming mode for multi-GB scrapes

## Installation
```bash
pip install metrics-cardinality-cli
```

## Usage
```bash
curl http://localhost:9090/metrics | metrics-cardinality-cli analyze --threshold 10000
metrics-cardinality-cli analyze --file metrics.txt --format json
```

## Architecture
Single-pass streaming parser + reservoir sampling for label cardinality estimation. No full metric storage.

## Alternatives considered
- promtool (no cardinality ranking)
- cardinality-exporter (requires running Prometheus)
- Manual PromQL inspection (too slow)

## Benchmarks
Processed 2.3M samples from real Kubernetes cluster in 1.8s on M2 MacBook.