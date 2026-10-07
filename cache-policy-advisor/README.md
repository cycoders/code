# cache-policy-advisor

## Why this exists
Production services waste money and deliver stale content because cache headers are set once and forgotten. This tool ingests real access logs, reconstructs cache behavior, and produces actionable, data-driven header recommendations.

## Features
- Parses combined, common, and JSON log formats
- Computes hit rate, freshness lifetime, and revalidation cost
- Recommends Cache-Control, Expires, and surrogate keys
- Supports configurable freshness windows and byte-cost models
- Exports machine-readable JSON for CI integration

## Installation
pip install cache-policy-advisor

## Usage
cache-policy-advisor analyze access.log --format combined --window 7d
cache-policy-advisor recommend --config policy.yaml

## Benchmarks
On a 2.3 GB nginx log (14 M requests) the tool finishes in 11 s with < 180 MB RSS.