# otel-sampling-advisor

## Why this exists
Distributed tracing generates enormous volumes of data. Most teams either over-sample (inflating costs) or under-sample (losing critical signals). otel-sampling-advisor ingests real trace data, models different sampling strategies, and produces actionable recommendations that protect error budgets while minimizing storage and processing spend.

## Features
- Ingests Jaeger JSON or OTLP protobuf trace exports
- Simulates tail, head, probability, and adaptive sampling
- Computes signal preservation, error budget impact, and cost deltas
- Generates ready-to-deploy OpenTelemetry Collector configuration snippets
- Rich progress reporting and deterministic simulation mode

## Installation
```bash
pip install otel-sampling-advisor
```

## Usage
```bash
otel-sampling-advisor analyze traces.json --strategy adaptive --budget 0.15
otel-sampling-advisor recommend traces/ --output collector.yaml
```

## Architecture
Core simulation engine uses a streaming trace processor with reservoir sampling. Strategy plugins are isolated and testable. All randomness is seeded for reproducibility.

## Alternatives considered
- Manual Collector config tuning: error-prone and slow
- Commercial APM sampling: vendor lock-in
- Simple probability sampling: loses important traces