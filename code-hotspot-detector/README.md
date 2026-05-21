# code-hotspot-detector

## Why this exists
Large codebases accumulate risk in files that are both complex and frequently changed. This tool surfaces those exact modules so teams can prioritize refactoring with maximum impact.

## Features
- Computes McCabe cyclomatic complexity per function and module
- Extracts churn (commit count + author count) from git history
- Produces a normalized risk score and ranked table
- Supports configurable time windows and file filters
- Exports JSON and CSV for CI integration
- Graceful handling of large monorepos with progress bars

## Installation
```bash
pip install code-hotspot-detector
```

## Usage
```bash
code-hotspot-detector --repo /path/to/repo --since 90d --top 30 --format table
```

## Architecture
The pipeline has three stages: git log extraction, AST-based complexity analysis, and statistical scoring. All heavy lifting uses only the Python standard library plus GitPython and radon for optional acceleration.

## Benchmarks
On a 120k LOC monorepo the tool completes in <12s on a laptop.

## Alternatives considered
- git log + manual complexity scripts: error-prone and slow
- CodeClimate / SonarQube: heavyweight and expensive for focused hotspot analysis