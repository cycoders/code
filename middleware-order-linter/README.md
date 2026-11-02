# middleware-order-linter

## Why this exists
Middleware ordering bugs are a silent source of security incidents and performance regressions. A single misplaced CORS, auth, or compression layer can leak data or add 50 ms to every request. This tool gives senior engineers a fast, deterministic way to catch these problems before they reach production.

## Features
- Framework-aware parsers for Flask, Django, FastAPI, Starlette, Express (via AST)
- Rule engine covering 25+ security and perf invariants (auth before CORS, compression after auth, rate-limit early, etc.)
- Precise line/column reporting with suggested fixes
- Configurable rule sets via YAML or inline comments
- CI-friendly exit codes and SARIF output

## Installation
```bash
pip install middleware-order-linter
```

## Usage
```bash
middleware-order-linter app.py --framework flask --format sarif
middleware-order-linter src/ --config .mware-lint.yaml
```

## Architecture
Two-pass design: lightweight AST extraction followed by a small rule engine. Rules are pure functions, making the tool trivial to extend.

## Benchmarks
Scans a 12 kLOC codebase in <120 ms on M2 MacBook Air.

## Alternatives considered
- semgrep (too generic, noisy)
- custom linters per framework (maintenance burden)

MIT License