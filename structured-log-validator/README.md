# structured-log-validator

## Why this exists
Production logs must conform to strict schemas for reliable parsing, alerting, and analytics. Manual inspection fails at scale. This CLI validates JSON/NDJSON logs against JSON Schema, reports violations with precise locations, and exits non-zero on errors.

## Features
- Full JSON Schema Draft 2020-12 support via jsonschema
- NDJSON streaming with progress bars
- Detailed violation reports (path, expected, actual)
- Configurable severity thresholds and exit codes
- Schema references and $ref resolution
- CI-friendly output formats (text, json)

## Installation
pip install structured-log-validator

## Usage
structured-log-validator validate --schema schema.json logs.ndjson

## Architecture
Validator uses streaming parser + jsonschema for memory efficiency. Reporter aggregates errors per file and per rule.

## Benchmarks
Validated 1M-line NDJSON in 4.2s on M2 Mac (p95 < 50µs/line).

## Alternatives considered
- log-schema-inferrer (inference only)
- generic jsonschema CLI (no streaming/reporting polish)