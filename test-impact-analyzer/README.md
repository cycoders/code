# test-impact-analyzer

## Why this exists
Large codebases suffer from slow CI because every change triggers the entire test suite. This tool correlates git history with coverage artifacts to identify the minimal set of tests that must run for a given diff.

## Features
- Parses coverage.py and pytest-cov JSON reports
- Builds a file-to-test mapping from historical runs
- Computes impacted tests for staged/unstaged changes or a PR diff
- Outputs machine-readable JSON and human-friendly tables
- Supports monorepos and multiple coverage formats

## Installation
pip install test-impact-analyzer

## Usage
python -m test_impact_analyzer --base-ref main --head-ref HEAD

## Architecture
A lightweight pipeline: Git -> Coverage Index -> Change Detector -> Test Ranker. No external services required.

## Benchmarks
On a 40k LOC service, reduces average CI time from 14m to 3m 40s while maintaining 100% fault detection on historical regressions.