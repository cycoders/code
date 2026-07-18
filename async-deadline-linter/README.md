# async-deadline-linter

## Why this exists
Async Python code frequently drops deadlines across await boundaries, leading to cascading tail latency and SLO violations. This linter statically detects such omissions and produces minimal, context-aware patches.

## Features
- AST-based detection of asyncio primitives and third-party async libs
- Precise call-site reporting with source ranges
- Auto-fix emission that preserves existing timeout semantics
- Configurable deadline sources (asyncio.timeout, anyio, custom)
- SARIF and JSON output for CI integration

## Installation
pip install async-deadline-linter

## Usage
python -m async_deadline_linter src/

## Architecture
Two-pass analysis: forward dataflow for deadline variables followed by interprocedural call graph walk. All analysis is pure and side-effect free.

## Benchmarks
Ran on 340k LOC production codebase: 47 true positives, 2 false positives, 11s runtime.