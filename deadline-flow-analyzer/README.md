# deadline-flow-analyzer

## Why this exists
In distributed and async systems, context deadlines frequently fail to propagate through call chains, leading to cascading timeouts, resource leaks, and unpredictable tail latencies. Manual review is error-prone at scale.

## Features
- Builds precise async call graphs from Python source
- Detects functions that accept deadlines but fail to forward them
- Supports asyncio, anyio, and common RPC client patterns
- Configurable via pyproject.toml or CLI flags
- Rich terminal output with source locations and suggested fixes
- Handles decorators, contextvars, and partial applications

## Installation
```bash
pip install deadline-flow-analyzer
```

## Usage
```bash
deadline-flow-analyzer src/
deadline-flow-analyzer . --config pyproject.toml --format json
```

## Architecture
Uses libcst for parsing, builds a lightweight call graph, then performs a reachability analysis for deadline parameters and contextvars. No runtime instrumentation required.

## Benchmarks
Analyzes a 50k LOC codebase in <800ms on M2 MacBook Pro.

## Alternatives considered
- pylint / ruff: lack semantic deadline tracking
- pyanalyze: too heavy for focused deadline checks
- Manual tracing: non-scalable