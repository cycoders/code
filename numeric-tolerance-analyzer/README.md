# numeric-tolerance-analyzer

## Why this exists
Floating-point comparisons in tests are a constant source of flakiness. Hard-coded tolerances like 1e-6 frequently fail on different hardware, Python versions, or BLAS implementations. This tool statically analyzes numerical code, tracks error propagation through expressions, and suggests the smallest safe tolerance for each comparison.

## Features
- AST-based analysis of NumPy, math, and pure Python numeric expressions
- Error bound propagation using interval arithmetic
- Support for common operations: add, mul, div, sqrt, dot, matmul
- Generates pytest.approx() or math.isclose() recommendations
- Configurable via pyproject.toml or CLI flags
- Reports with severity and suggested fixes

## Installation
```bash
pip install numeric-tolerance-analyzer
```

## Usage
```bash
numeric-tolerance-analyzer src/
numeric-tolerance-analyzer tests/ --format json --min-tol 1e-12
```

## Architecture
Lightweight static analyzer built on libcst. No runtime execution. Fast enough for pre-commit hooks.

## Alternatives considered
- pytest.approx defaults (too coarse)
- hypothesis (property based, complementary but heavier)
- Manual interval tracking (error-prone at scale)
