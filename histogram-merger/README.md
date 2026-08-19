# histogram-merger

## Why this exists
Accurate global p50/p95/p99 latency requires merging histograms across services and nodes. Shipping raw samples is expensive; naive addition of bucket counts produces incorrect percentiles. histogram-merger implements correct DDSketch merging with support for HDR Histogram and Prometheus-style histograms.

## Features
- Merge any number of DDSketch, HDR, or Prometheus histograms
- Streaming merge with bounded memory
- Exact p99 computation with configurable error
- CLI, library API, and stdin/stdout pipeline support
- JSON, binary, and Prometheus text format I/O
- Zero external services or paid APIs

## Installation
```bash
pip install histogram-merger
```

## Usage
```bash
# Merge files
histogram-merger merge *.hdr --p99 --output global.json

# Streaming
cat node-*.json | histogram-merger stream --error 0.01
```

## Architecture
Core merging logic lives in src/histogram_merger/merge.py using a DDSketch implementation with base-2 exponential buckets. Format adapters convert HDR and Prometheus histograms into the common sketch before merge. All operations are streaming and O(n) where n is number of buckets.

## Benchmarks
Merging 5000 1M-sample HDR histograms (p99 error <1%) completes in <800 ms on M2 MacBook Pro.

## Alternatives considered
- hdrhistogram: no multi-format merge
- prometheus/client_python: only local aggregation
- statsd: lossy downsampling

## License
MIT