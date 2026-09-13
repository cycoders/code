# cli-startup-analyzer

## Why this exists
CLI tools frequently suffer from slow startup due to heavy imports, side-effecting top-level code, and expensive initialization. Developers need precise, reproducible measurements and targeted suggestions rather than generic profiling.

## Features
- Measures wall time, CPU time, and import graph for the full startup path
- Identifies the slowest 10 imports with cumulative cost
- Detects top-level I/O, network, or subprocess calls during import
- Suggests lazy import locations and module split opportunities
- Supports both single-shot and multi-run statistical analysis
- Exports JSON, Markdown, or flamegraph-compatible data

## Installation
```bash
pip install cli-startup-analyzer
```

## Usage
```bash
python -m cli_startup_analyzer mycli -- --version
python -m cli_startup_analyzer mycli --runs 5 --format json
```

## Architecture
Uses a lightweight tracing import hook + subprocess isolation to avoid contaminating the analyzer's own environment. Results are aggregated with median + p95.

## Alternatives considered
- cProfile: too noisy for import phase
- py-spy: requires elevated privileges and lacks import granularity
- importtime: lacks recommendations and statistical aggregation
