# capacity-forecaster

## Why this exists
Senior engineers repeatedly face the same painful question: "Will our current resources last until the next procurement cycle?" Existing monitoring shows past usage; capacity-forecaster turns that data into defensible forecasts with confidence intervals and what-if scenarios.

## Features
- Ingests Prometheus, CloudWatch, or CSV time series
- Multiple growth models (linear, exponential, seasonal)
- Monte Carlo simulation for uncertainty
- Scenario comparison (traffic spike, new feature, cost optimization)
- Exports clean Markdown reports and Grafana dashboards
- Zero external API dependencies

## Installation
```bash
pip install -e .
```

## Usage
```bash
capacity-forecaster forecast --input metrics.csv --horizon 90d --model seasonal
```

## Architecture
Clean separation between ingestion, modeling, simulation, and reporting layers. All models are deterministic given the same seed.

## Benchmarks
Forecasts 10k-point series in <800ms on laptop CPU. Monte Carlo (10k runs) completes in 4.2s.

## Alternatives considered
- Custom spreadsheets: error-prone and non-reproducible
- Vendor tools: lock-in and opaque models
- Simple linear regression scripts: ignore seasonality and uncertainty