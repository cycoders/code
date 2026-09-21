# typosquat-auditor

## Why this exists
Typosquatting in PyPI remains a persistent supply-chain risk. Manual review of hundreds of dependencies is impractical. This tool provides fast, local, deterministic detection of suspiciously similar package names with zero external API calls.

## Features
- Levenshtein + Jaro-Winkler hybrid similarity
- Cluster analysis with configurable threshold
- Maintainer signal heuristics (no network)
- SARIF + JSON + human-readable output
- Works on requirements.txt, pyproject.toml, and pip freeze output

## Installation
pip install typosquat-auditor

## Usage
python -m typosquat_auditor -r requirements.txt --threshold 0.82 --format sarif

## Benchmarks
Scans 1200 dependencies in <180ms on M2 Mac.

## Alternatives considered
- pip-audit (focuses on known vulns)
- guarddog (requires network)

MIT licensed.