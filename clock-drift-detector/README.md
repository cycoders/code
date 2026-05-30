# clock-drift-detector

## Why this exists
Clock skew is a silent killer in distributed systems. Subtle drift between nodes produces mysterious ordering violations, duplicate processing, and broken causal chains that are nearly impossible to reproduce. Existing monitoring rarely surfaces the problem until it has already caused data loss or outages.

clock-drift-detector ingests timestamped events from multiple sources, aligns them using a shared correlation key, and produces statistically rigorous skew measurements with confidence intervals.

## Features
- Multi-source timestamp ingestion (JSON logs, Prometheus, CSV)
- Robust outlier-resistant skew estimation (Theil-Sen + RANSAC)
- Automatic detection of NTP/PTP anomalies and leap-second effects
- Exportable HTML report with interactive timeline and histogram
- CI-friendly exit codes and JUnit XML output

## Installation
```bash
pip install clock-drift-detector
```

## Usage
```bash
clock-drift-detector analyze \
  --sources node1.log node2.log node3.metrics \
  --key trace_id --ts-field ts \
  --report drift.html
```

## Architecture
Parser → Normalizer → Pairwise comparator → Robust estimator → Reporter. All components are streaming and memory-bounded.

## Benchmarks
On 2.3 M events across 17 nodes the tool produces results in <4 s with <0.3 ms error vs ground-truth PTP.

## Alternatives considered
- `chrony` / `ntpd` logs: too low-level
- Commercial APM: expensive and opaque
- Custom scripts: brittle and non-reproducible