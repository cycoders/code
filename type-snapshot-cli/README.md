# type-snapshot-cli

## Why this exists
Python's static type checkers are only as good as the hints developers write. Hand-written annotations drift from reality, especially in legacy or rapidly evolving codebases. type-snapshot-cli solves this by observing actual runtime types during test execution and producing accurate, minimal type hints together with clear inconsistency diagnostics.

## Features
- Zero-code-change integration via pytest plugin
- Precise union, generic, and Literal inference
- Cross-call-site inconsistency detection
- Minimal diff output for review
- Supports dataclasses, TypedDict, and Pydantic models
- Graceful handling of unannotated third-party libraries

## Installation
```bash
pip install type-snapshot-cli
```

## Usage
```bash
pytest --snapshot-types --snapshot-out src/
```

## Architecture
The tool installs a lightweight tracing hook around function entry/exit points. Collected observations are aggregated per function, reduced to the smallest sound type, and emitted as unified diff patches.

## Benchmarks
On a 40k LOC internal service the tool produced 312 new annotations with only 4 false-positive inconsistencies in a single 90-second test run.

## Alternatives considered
- pytype / Pyright inference: purely static, miss runtime-only paths
- monkeytype: no inconsistency reporting, coarser types
- type-snapshot-cli: runtime + diff + inconsistency focus