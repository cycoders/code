# bidi-text-security-cli

## Why this exists
Unicode bidirectional (bidi) override characters enable sophisticated supply-chain attacks by visually reordering source code while preserving its logical execution order. Senior engineers need a fast, reliable way to scan repositories, pull requests, and configuration before they reach production.

## Features
- Scans entire directory trees for bidi override characters (LRE, RLE, LRO, RLO, PDF, LRI, RLI, FSI, PDI)
- Reports exact file, line, column, and character code with context
- Classifies risk level (high/medium) based on surrounding syntax
- Suggests safe rewrites that preserve intended logic
- Supports .gitignore and configurable ignore patterns
- JSON, SARIF, and human-readable output formats
- Streaming mode for CI pipelines with non-zero exit on findings

## Installation
```bash
pip install bidi-text-security-cli
```

## Usage
```bash
bidi-text-security-cli scan .
bidi-text-security-cli scan src/ --format sarif --fail-on high
bidi-text-security-cli rewrite vulnerable.py --in-place
```

## Architecture
Pure-Python scanner using Unicode character properties and a small state machine for context classification. No external dependencies beyond the standard library and rich for terminal output.

## Benchmarks
Scans the CPython source tree (~500k LOC) in <800 ms on a 2023 MacBook Pro.

## Alternatives considered
- grep-based approaches miss context and produce noisy results
- ESLint unicode-bidi plugin only covers JavaScript
- Manual review is impractical at scale