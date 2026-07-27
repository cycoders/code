# tracecontext-validator

## Why this exists
Distributed tracing breaks silently when services fail to propagate traceparent/tracestate headers correctly. Engineers lose hours correlating logs across microservices. This tool validates propagation at the edge and in logs, surfaces exact violations, and provides actionable fixes.

## Features
- Strict W3C Trace Context parsing and validation
- CLI for live HTTP traffic, HAR files, and log streams
- Detects missing, malformed, or mutated trace IDs
- Supports traceparent v0 and tracestate key-value rules
- Zero-config, works offline, pure Python

## Installation
```bash
pip install tracecontext-validator
```

## Usage
```bash
# Validate a single request
tracecontext-validator check --header 'traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01'

# Scan a HAR file
tracecontext-validator scan-har requests.har

# Tail logs for propagation issues
tracecontext-validator watch --format json
```

## Architecture
Header parsing in `core.py` follows the W3C spec exactly. Violations are classified into error, warning, and info categories with line numbers and suggested patches.

## Benchmarks
Scans 10k headers/sec on modest hardware. Memory usage < 15 MiB.

## Alternatives considered
- Manual header inspection: error-prone
- Commercial APMs: expensive and noisy
- Existing tracers: focus on emission, not validation
