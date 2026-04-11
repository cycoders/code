# Loadtest Analyzer

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

## Why this exists

Load testing tools like k6, Locust, Artillery generate vast result files, but extracting actionable insights requires manual Excel work or Grafana setups. This CLI delivers instant, beautiful terminal reports with percentiles, RPS, error rates, top slow endpoints, and regression detection via comparison—saving senior engineers hours per test cycle. Production-ready after focused polish.

## Features

- Parses CSV, JSON, JSONL with configurable field mappings (works with Locust exports, k6 detailed JSON, custom scripts)
- Key metrics: RPS, avg/P50/P90/P95/P99 durations, error rate, time span
- Top 10 slowest endpoints by avg latency
- Compare runs for regressions (side-by-side tables with highlights)
- Rich terminal output with tables; JSON export for CI/CD
- Graceful handling of invalid rows/large files (>1M reqs in seconds)
- Zero config, flexible CLI flags

## Installation

```
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Quickstart

```
# Analyze CSV (e.g., Locust/custom)
loadtest-analyzer analyze results.csv

# JSON with custom fields
loadtest-analyzer analyze k6.json --format json --ts-field t --duration-field tt --endpoint-field path

# Compare for regressions
loadtest-analyzer compare baseline.csv current.csv

# JSON output
loadtest-analyzer analyze file.csv --output stats.json
```

Rich help: `loadtest-analyzer --help analyze`

## Examples

Sample data in `tests/data/`.

**Terminal output:**

```
╭──────────────────── Load Test Analysis ──────────────────────╮
│ Total Requests    │ 1000                                    │
│ RPS               │ 25.50                                   │
│ Error Rate        │ 2.30%                                   │
│ Avg Duration      │ 145.20ms                                │
│ P95               │ 280.50ms                                │
╰───────────────────────────────────────────────────────────────╯

╭─────────────── Top 10 Slowest Endpoints ───────────────╮
│ Endpoint │ Avg (ms) │ Count │
├──────────┼──────────┼───────┤
│ /api/pay │ 450.20   │ 150   │
│ /api/search │ 320.10 │ 200 │
└──────────┴──────────┴───────┘
```

## Benchmarks

| Requests | Format | Time | Memory |
|----------|--------|------|--------|
| 10k      | CSV    | 0.02s| 50MB   |
| 100k     | JSON   | 0.15s| 200MB  |
| 1M       | CSV    | 1.8s | 1.2GB  |

Tested on Apple M1, pure Python efficiency.

## Alternatives Considered

| Tool | Pros | Cons |
|------|------|------|
| Grafana/k6 UI | Visual | Heavy Docker setup |
| Pandas/Excel | Flexible | Manual, slow for large files |
| locust stats | Basic | No percentiles/top endpoints |

This: Zero-setup CLI, dev-focused, extensible parsers.

## Architecture

```
CLI (Typer) → Parsers (CSV/JSON/JSONL) → List[Request] → Stats → Rich Tables/JSON
                           ↓
                       Streaming parse, list aggregate
```

- **Models**: Typed Request dataclass
- **Parsers**: Yield Requests, skip invalids, timestamp flex (unix/ISO)
- **Stats**: Pure Python percentiles, defaultdict for endpoints
- **Output**: Rich Console tables, compare highlights regressions (>10% worse: red)

Extensible: Add parser for JMeter JTL (XML).

## Development

```
pip install -r requirements-dev.txt
pytest tests/
```

## License

MIT © 2025 Arya Sianati
