# observability-gap-detector

## Why this exists
Senior engineers ship services that are impossible to debug in production because instrumentation was added ad-hoc. This tool statically analyzes a Python codebase and produces a concise, prioritized report of missing logging, metrics, and tracing at call sites that matter.

## Features
- AST-based detection of functions, HTTP handlers, background tasks and DB queries
- Scoring model that ranks gaps by blast radius and criticality
- Generates ready-to-apply unified diff patches for OpenTelemetry + structlog
- Respects existing instrumentation and never double-instruments
- CI-friendly JSON and SARIF output

## Installation
pip install observability-gap-detector

## Usage
observability-gap-detector scan ./src --format sarif --output gaps.sarif

## Architecture
Lightweight visitor pattern over libcst, deterministic scoring, zero runtime overhead.

## Benchmarks
Scans 120k LOC in <800 ms on M2 MacBook Pro.

## Alternatives considered
- Manual code review: too slow
- Runtime coverage tools: miss static paths
- Generic linters: lack observability domain knowledge