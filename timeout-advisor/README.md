# timeout-advisor

## Why this exists
Production timeouts are almost always chosen by gut feel. Too low and you create cascading failures under tail latency. Too high and you waste resources and slow down incident response. timeout-advisor turns latency histograms (from traces, logs, or Prometheus) into statistically grounded timeout recommendations that balance p99 safety with responsiveness.

## Features
- Multiple input formats: Jaeger/OTLP JSON, Prometheus histograms, plain latency CSVs
- Percentile-aware analysis with configurable safety margins
- Circuit-breaker and retry budget awareness
- Generates both client and server timeout suggestions
- Exports Grafana dashboard panels and SLO burn-rate alerts
- Zero external API dependencies

## Installation
```bash
pip install timeout-advisor
```

## Usage
```bash
# From OTLP trace export
curl -s http://jaeger:16686/api/traces | timeout-advisor --input otlp --p99-margin 0.2

# From Prometheus
timeout-advisor --input prometheus --metric http_request_duration_seconds --quantile 0.99
```

## Architecture
Pure Python 3.11+ with numpy for histogram math, rich for output, and typer for CLI. All algorithms are deterministic and fully tested.

## Alternatives considered
- Manual p99 reading in Grafana (error-prone)
- Hardcoded 30s timeouts (wasteful)
- Commercial APM suggestions (vendor lock-in)