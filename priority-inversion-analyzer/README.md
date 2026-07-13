# priority-inversion-analyzer

## Why this exists
Priority inversion silently degrades latency and throughput in concurrent systems. Existing tools focus on runtime profiling or OS-level detection; developers need fast, early feedback directly from source.

## Features
- Static analysis of threading.Lock, asyncio.Lock, and semaphore usage
- Detects classic, bounded, and chained inversion patterns
- Prioritizes findings by estimated impact using call-graph depth
- Supports Python 3.11+ with full type annotations
- Rich terminal output with remediation guidance
- Configurable via pyproject.toml or CLI flags

## Installation
```bash
pip install priority-inversion-analyzer
```

## Usage
```bash
python -m priority_inversion_analyzer src/
python -m priority_inversion_analyzer --format json --threshold high .
```

## Architecture
Uses libcst for AST traversal, builds a lightweight lock-acquisition graph, then applies cycle and priority-path detection. Zero runtime instrumentation required.

## Benchmarks
Analyzes 50k LOC in <800 ms on M2 MacBook Pro.

## Alternatives considered
- pylint concurrency plugins (too shallow)
- thread-sanitizer (runtime only)
- custom ruff rules (insufficient graph analysis)
