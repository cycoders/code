# float-precision-linter

## Why this exists
Floating-point arithmetic silently produces incorrect results in scientific computing, ML pipelines, and financial systems. Existing linters catch style issues but miss numeric instability.

## Features
- AST-based detection of common patterns (sum, mean, comparisons, matrix ops)
- Configurable epsilon and tolerance via CLI, pyproject.toml or env vars
- Suggestions for stable alternatives (math.fsum, decimal, numpy.isclose)
- Progress bar and structured JSON output
- 5+ core test cases with edge coverage

## Installation
pip install float-precision-linter

## Usage
python -m float_precision_linter src/

## Benchmarks
Analyzes 50k LOC in <800 ms on M2 Mac.

## Alternatives considered
- pylint numeric plugins: too noisy
- mypy: no runtime numeric semantics
- manual review: not scalable