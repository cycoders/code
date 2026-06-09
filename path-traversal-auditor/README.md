# path-traversal-auditor

## Why this exists
Path traversal vulnerabilities remain one of the most common and dangerous classes of security issues in Python web applications and CLIs. Existing linters catch only the most obvious cases. This tool performs precise interprocedural taint tracking to find real exploitable flows.

## Features
- AST-based taint analysis with flow sensitivity
- Support for os.path, pathlib, and common web frameworks
- Configurable sources, sinks and sanitizers
- SARIF and JSON output for CI integration
- Low false positive rate through context tracking

## Installation
pip install path-traversal-auditor

## Usage
path-traversal-auditor scan .
path-traversal-auditor scan app/ --format sarif --output report.sarif

## Architecture
See docs/architecture.md
