# benchstat-cli

## Why this exists
Benchmark numbers lie without statistics. Engineers ship performance regressions because they eyeball noisy results. benchstat-cli brings Go's benchstat rigor to any language by parsing common output formats, computing confidence intervals, and flagging real changes.

## Features
- Parses Go, Python (pytest-benchmark), and custom JSON formats
- Computes mean, median, min, max, stddev, and 95% confidence intervals
- Delta detection with user-configurable significance threshold
- Beautiful terminal tables and machine-readable JSON/CSV output
- Supports multiple iterations and geometric mean across suites

## Installation
```bash
pip install benchstat-cli
```

## Usage
```bash
benchstat before.txt after.txt
benchstat --format json --threshold 0.03 suite1.json suite2.json
```

## Architecture
Single-pass streaming parser + numpy for statistics. Zero external services.

## Alternatives considered
- benchstat (Go): excellent but language-specific
- custom scripts: error-prone and lack confidence math

MIT licensed, 100% offline.