# blast-radius-cli

## Why this exists
Code reviews and test planning suffer from incomplete mental models of change impact. Engineers waste time on low-risk diffs or miss critical downstream effects. blast-radius-cli builds an accurate call graph from static analysis, computes the transitive closure of affected symbols, and produces a ranked list of impacted modules, tests, and services.

## Features
- Precise Python call-graph construction via AST + import resolution
- Transitive blast-radius scoring with configurable depth and weighting
- Test impact prediction using coverage mapping (optional)
- SARIF and JSON output for CI integration
- Rich terminal rendering with progress bars and tree views
- Configuration via pyproject.toml or CLI flags

## Installation
```bash
pip install blast-radius-cli
```

## Usage
```bash
blast-radius diff HEAD~1 --format rich
blast-radius diff main...feature --json | jq '.impacted_tests'
```

## Architecture
Single-pass AST walker collects definitions and references. A directed graph is materialized in memory. Dijkstra-style traversal from changed symbols yields the radius. All algorithms are deterministic and pure.

## Alternatives considered
- pydeps / pylint: coarser module-level only
- CodeQL / Semgrep: heavier, language-specific rules
- IDE language servers: not scriptable in headless CI

## Benchmarks
On a 120k LOC monorepo, cold run completes in <800 ms with <180 MB RSS.