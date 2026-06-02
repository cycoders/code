# test-minimizer-cli

## Why this exists

Debugging a failing test with hundreds of lines or complex fixtures wastes hours. This tool applies delta debugging to systematically reduce the test to the minimal failing case while preserving the original failure.

## Features
- Delta-debugging core reducer with configurable granularity
- Support for pytest, unittest and plain Python functions
- Parallel reduction with progress reporting
- Diff output and minimal reproducer export
- Handles environment, fixtures and parameterization

## Installation

```bash
pip install test-minimizer-cli
```

## Usage

```bash
python -m test_minimizer_cli tests/test_billing.py::test_invoice_flow --parallel 4
```

## Architecture
Core reducer in `minimizer.py` implements the classic delta-debugging algorithm with safe test execution sandboxing. CLI built on Typer + Rich.

## Alternatives considered
- Manual binary search: error-prone and slow
- Existing fuzzers: too heavy and language-specific

MIT licensed, production quality.