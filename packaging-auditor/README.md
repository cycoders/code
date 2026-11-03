# packaging-auditor

## Why this exists
Packaging Python projects remains surprisingly error-prone. Missing classifiers, incorrect entry points, or an incomplete pyproject.toml silently break installs for downstream users. packaging-auditor statically analyzes a project and reports concrete, prioritized issues that affect distribution and long-term maintainability.

## Features
- Validates pyproject.toml, setup.cfg, and setup.py for completeness and correctness
- Detects missing or incorrect metadata (license, readme, classifiers, urls)
- Checks entry points, scripts, and package discovery rules
- Flags common publishing blockers (wheel vs sdist mismatches, missing license files)
- Produces machine-readable JSON output for CI integration
- Zero network calls; works entirely offline

## Installation
```bash
pip install packaging-auditor
```

## Usage
```bash
packaging-auditor .
packaging-auditor path/to/project --format json --fail-on error
```

## Architecture
Uses tomllib + configparser for config parsing, importlib.metadata for validation rules, and a rule engine with severity levels. All checks are deterministic and version-pinned.

## Benchmarks
Runs in <80 ms on a 50-file project. Tested against 120 real-world PyPI packages.

## Alternatives considered
- twine check (only validates after build)
- check-manifest (narrower scope)
- pyroma (less granular, no CI-friendly output)
