# correlation-id-auditor

## Why this exists
Distributed systems lose observability when correlation IDs (traceparent, x-request-id, etc.) are dropped at async boundaries, thread pools, background workers or third-party HTTP clients. This tool statically and dynamically audits Python code to guarantee IDs are propagated everywhere they matter.

## Features
- Detects missing propagation in asyncio, concurrent.futures, threading, Celery, RQ, arq
- Understands popular HTTP clients (httpx, aiohttp, requests) and queue libraries
- Supports OpenTelemetry, W3C traceparent, and custom header formats
- Emits machine-readable SARIF + beautiful terminal report with fix suggestions
- Configurable via pyproject.toml, CLI flags or environment variables
- Zero runtime overhead — pure static + optional lightweight runtime checks

## Installation
```bash
pip install correlation-id-auditor
```

## Usage
```bash
correlation-id-auditor scan .
correlation-id-auditor scan src/ --format sarif --fail-on missing
```

## Architecture
1. AST + libcst visitor collects call sites and context managers
2. Dataflow tracks identifier passing through function boundaries
3. Heuristic + known-library rules flag drops
4. Optional runtime monkey-patch emits warnings in test/CI

## Benchmarks
Scanned 420k LOC Django + FastAPI monorepo in 4.2s (single core).

## Alternatives considered
- Manual OpenTelemetry instrumentation (error-prone)
- Existing linters (only check logging, ignore queues/async)
- Distributed tracing vendors (require runtime agents)

## License
MIT