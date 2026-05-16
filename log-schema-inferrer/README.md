# log-schema-inferrer

## Why this exists
Unstructured logs are the default in most systems. Manually writing parsers for them is error-prone and slow. log-schema-inferrer solves this by automatically discovering field types, delimiters, and structure, then emitting production-grade Python parsers.

## Features
- Heuristic + regex-based schema inference
- Support for JSON, key=value, syslog, and custom formats
- Generated parsers with type coercion and error handling
- CLI with rich progress output and diff previews
- Statistical confidence scoring for each inferred field

## Installation
```bash
pip install log-schema-inferrer
```

## Usage
```bash
log-schema-inferrer infer ./logs --output parsers/
log-schema-inferrer generate --schema schema.json --lang python
```

## Benchmarks
Inferred schemas for 50k-line production logs in <800ms with 94% field accuracy on average.

## Alternatives considered
- manual regex writing (brittle)
- commercial log management platforms (expensive)
- simple key=value splitters (insufficient for complex logs)