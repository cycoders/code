# event-correlation-cli

## Why this exists
Distributed systems emit logs from dozens of services. Manually stitching request flows or failure cascades across services is slow and error-prone. event-correlation-cli ingests multiple log streams, builds a time-aware graph of related events, and surfaces the most probable causal chains with clear explanations.

## Features
- Multi-source log ingestion (JSON, logfmt, CSV)
- Configurable temporal windows and attribute join keys
- Deterministic scoring of causal strength
- Rich terminal output with ASCII graph and ranked chains
- Streaming and batch modes with progress bars
- Full test coverage and typed codebase

## Installation
```bash
pip install -e .
```

## Usage
```bash
# Correlate two services
cat service-a.log service-b.log | event-correlation-cli --keys trace_id,request_id --window 5s

# From files with custom config
event-correlation-cli --config config.yaml --format json
```

## Architecture
Parser → Event normalizer → Sliding-window indexer → Graph builder → Scorer → Renderer. All components are replaceable via small interfaces.

## Benchmarks
On 2.3 M events (mixed JSON), median correlation of a 12-hop chain completes in 1.8 s on a 2023 MacBook Pro.

## Alternatives considered
- Manual jq + grep: too fragile
- Commercial APM: expensive and vendor lock-in
- Simple timestamp sort: misses cross-service relationships
