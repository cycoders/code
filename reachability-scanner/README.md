# reachability-scanner

## Why this exists
Vulnerability scanners report hundreds of CVEs. Most are unreachable from your application entry points. This tool builds an accurate static call graph for Python packages and answers: "can this vulnerable function actually be executed?"

## Features
- AST-based intra- and inter-module call graph construction
- Configurable entry points (CLI, web handlers, tests)
- Precise reachability queries against known vulnerable symbols
- SARIF + JSON output for CI integration
- Graceful handling of dynamic code and stdlib

## Installation
```bash
pip install reachability-scanner
```

## Usage
```bash
reachability-scanner scan . --entry src/app.py:main --vuln-db advisories.json
```

## Architecture
Single-pass AST walker builds a directed graph stored in networkx. Reachability uses DFS/BFS from declared roots. No runtime execution.

## Benchmarks
Scanned 180k LOC Django codebase in 2.8s; reduced 312 advisories to 7 reachable ones.

## Alternatives considered
- bandit / semgrep (pattern only)
- osv-scanner (no reachability)
- pyright / mypy (type focus, no graph)
