# trace-cost-analyzer

## Why this exists
Distributed tracing is essential yet expensive. Most teams discover they are spending thousands per month only after the bill arrives. trace-cost-analyzer gives a fast, accurate forecast of span volume and cost before you deploy or change sampling.

## Features
- Ingests OpenTelemetry, Jaeger, or Zipkin trace samples
- Supports pricing models from Datadog, Honeycomb, New Relic, Grafana Cloud, Lightstep
- Configurable sampling, span attributes, and error budgets
- Produces human-readable report + machine-readable JSON
- Handles head-based, tail-based, and probabilistic sampling

## Installation
```bash
pip install trace-cost-analyzer
```

## Usage
```bash
trace-cost-analyzer --input sample-traces.json --vendor honeycomb --config pricing.yaml
```

## Architecture
Single-pass streaming parser + pluggable vendor pricing engine. No external services required.

## Alternatives considered
- Manual spreadsheet math: error-prone and stale
- Vendor calculators: require account login and hide assumptions
- Full OTEL collector: overkill for cost modeling