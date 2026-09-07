# license-compat-cli

## Why this exists
License conflicts in dependency trees cause legal and compliance headaches at release time. Most tools only list licenses; few detect transitive incompatibilities or suggest concrete fixes.

## Features
- Parses lockfiles and manifests for Python, Node, Go, Rust
- Models SPDX license expressions and common compatibility matrix
- Reports direct and transitive conflicts with severity
- Suggests minimal version bumps or alternative packages
- Fast, offline, zero external APIs

## Installation
```bash
pip install license-compat-cli
```

## Usage
```bash
license-compat-cli .
license-compat-cli --format json /path/to/project
```

## Architecture
Core uses a small SPDX expression parser + precomputed compatibility DAG. Lockfile readers are pluggable. All data lives in a compact JSON resource file.

## Benchmarks
Scans a 1200-package tree in <800 ms on M2 laptop.

## Alternatives considered
- FOSSology: heavy, requires database
- ClearlyDefined: online only
- pip-licenses: no compatibility logic
