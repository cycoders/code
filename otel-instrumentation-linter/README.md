# otel-instrumentation-linter

## Why this exists
Production systems routinely ship with incomplete OpenTelemetry coverage. Missing spans, incorrect attribute semantics, and absent metrics make distributed tracing unreliable. This linter gives senior engineers a fast, local way to enforce instrumentation contracts before code reaches staging.

## Features
- Detects missing @tracer.start_as_current_span and manual span creation
- Validates semantic conventions for HTTP, DB, and messaging spans
- Reports absent metric instruments (counters, histograms) on hot paths
- Understands FastAPI, Django, SQLAlchemy, Celery, and requests out of the box
- Configurable via .otel-lint.toml or pyproject.toml
- Beautiful rich terminal output with fix suggestions

## Installation
pip install otel-instrumentation-linter

## Usage
otel-instrumentation-linter .
otel-instrumentation-linter src/ --config pyproject.toml --fail-on warnings

## Architecture
Static AST analysis + lightweight semantic pattern matching. No runtime required. See docs/architecture.md.

## Benchmarks
Scans 50k LOC in <800 ms on M2 MacBook Pro.

## Alternatives considered
- Semgrep rules: too noisy, no Python-native semantic model
- OpenTelemetry collector policies: only catch issues at runtime
- Manual reviews: do not scale