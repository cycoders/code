# cron-overlap-detector

## Why this exists
Production systems frequently suffer from silent resource contention when multiple cron jobs or systemd timers execute concurrently. This tool statically analyzes crontab files and timer units, computes precise execution windows over a configurable horizon, and reports overlaps with severity scoring.

## Features
- Parses standard crontab syntax plus systemd timer calendar expressions
- Computes exact execution intervals with timezone awareness
- Detects overlaps with configurable tolerance windows
- Supports include/exclude patterns and severity thresholds
- Beautiful Rich tables and JSON output for CI integration
- Handles daylight-saving transitions correctly

## Installation
```bash
pip install cron-overlap-detector
```

## Usage
```bash
cron-overlap-detector /etc/cron.d/ --horizon-days 7 --format table
cron-overlap-detector timers/ --json | jq '.overlaps[]'
```

## Architecture
Core engine uses datetime recurrence expansion limited to the horizon, followed by interval tree overlap queries for O(n log n) performance.

## Alternatives considered
- cron-simulator (runtime only)
- cron-explainer (no overlap detection)
- Manual spreadsheet analysis (error-prone)

## Benchmarks
Analyzes 1200+ jobs across 14 crontabs in <800 ms on modest hardware.