# latency-budget-allocator

## Why this exists
Distributed systems rarely meet their SLOs because latency budgets are assigned arbitrarily. This tool ingests a service dependency graph and target p99 SLO, then produces an optimal, enforceable per-hop budget allocation with safety margins and validation against real traces.

## Features
- Parses OpenTelemetry traces or static service graphs
- Computes budget allocations using a constrained optimization model
- Emits enforceable budget YAML for circuit breakers and clients
- Validates historical traces against proposed budgets
- Reports headroom, risk hotspots, and suggested improvements

## Installation
```bash
pip install latency-budget-allocator
```

## Usage
```bash
latency-budget-allocator allocate --graph services.yaml --slo 250ms --output budgets.yaml
latency-budget-allocator validate --traces traces.jsonl --budgets budgets.yaml
```

## Architecture
Core algorithm uses a linear program solved via scipy to minimize maximum utilization subject to the end-to-end SLO and per-service minimum budgets. Results are deterministic given the same inputs.

## Alternatives considered
Manual spreadsheets, ad-hoc scripts, and commercial APM features all lack reproducible allocation and validation against traces.