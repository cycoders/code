# error-budget-cli

## Why this exists
SLO error budget tracking is essential for SRE teams but existing tools are either spreadsheet-based or buried inside heavy observability platforms. This CLI provides instant, reproducible error budget calculations, burn-rate projections, and risk flagging directly from the terminal.

## Features
- Compute remaining error budget from SLI measurements
- Multi-window burn rate analysis (1h, 6h, 1d, 3d)
- Project time-to-exhaustion with confidence intervals
- Support for both time-based and request-based SLOs
- Export to JSON, CSV, or Markdown reports
- Sensible defaults aligned with Google SRE workbook

## Installation
```bash
pip install error-budget-cli
```

## Usage
```bash
error-budget-cli compute --target 99.9 --total 1000000 --bad 120
error-budget-cli burn --sli-file metrics.json --windows 1h,6h,1d
```

## Architecture
Pure Python, zero external services. Calculations follow the standard error budget formula and burn-rate threshold recommendations from the SRE books.

## Alternatives considered
- Custom spreadsheets: error-prone and non-reproducible
- Datadog/New Relic SLO modules: vendor lock-in and high cost
- Prometheus recording rules: powerful but require running a full stack