# alert-rule-tester

## Why this exists
Prometheus alerting rules are notoriously difficult to get right. A single misconfigured `for` duration, missing label, or wrong threshold produces either constant noise or dangerous silence. Existing linters only check syntax. This tool replays real metrics against rules and reports firing behavior, edge cases, and blast radius.

## Features
- Parses and type-checks PromQL expressions
- Replays metrics from VictoriaMetrics/Prometheus remote-read or local TSDB samples
- Simulates `for` durations and label matching exactly as Prometheus does
- Detects high-churn label combinations that explode cardinality
- Produces a machine-readable report with firing timeline and suggested fixes
- Works offline with recorded samples

## Installation
```bash
pip install alert-rule-tester
```

## Usage
```bash
alert-rule-tester rules/ --metrics samples.jsonl --since 7d
```

## Architecture
Core engine mirrors Prometheus rule evaluation semantics using a streaming evaluator. Metrics are indexed by series for O(1) lookup during simulation. All heavy lifting stays in pure Python with numpy for vector operations.

## Alternatives considered
- promtool: only static checks
- Thanos ruler: requires running cluster
- Custom scripts: brittle and non-reproducible

## Benchmarks
500 rules × 30 days of 1m-resolution metrics: 4.2s on M2 MacBook Pro.
