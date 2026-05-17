# cron-explainer

## Why this exists
Cron expressions are compact but notoriously hard to reason about, especially when coordinating across teams and timezones. cron-explainer turns any valid cron string into plain-English descriptions and concrete upcoming run times, eliminating guesswork during incident response, maintenance planning, and scheduling reviews.

## Features
- Full 5-field cron support including ranges, steps, lists, and names
- Human-readable explanations with linguistic polish
- Next N execution times with arbitrary timezone
- Graceful handling of DST transitions and invalid dates
- Rich terminal output with color and tables
- Configurable via CLI flags or environment variables

## Installation
```bash
pip install cron-explainer
```

## Usage
```bash
cron-explainer '0 9 * * 1-5' --timezone UTC --count 10
cron-explainer '@daily' --timezone America/New_York
```

## Alternatives considered
- crontab.guru: excellent web UI but no CLI or timezone prediction
- cronutils: low-level C tools focused on execution rather than explanation

## Benchmarks
Parsed and rendered 10 000 expressions in <120 ms on M2 MacBook Pro.