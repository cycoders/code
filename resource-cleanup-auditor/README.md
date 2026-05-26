# resource-cleanup-auditor

## Why this exists
Resource leaks from unclosed files, sockets, and database connections remain a top source of production incidents. Manual audits are error-prone and existing linters miss nuanced patterns involving conditional paths and custom wrappers.

## Features
- AST-based detection of raw resource acquisition without context managers
- Support for custom cleanup functions and contextlib helpers
- Precise reporting with line numbers and suggested fixes
- Configurable allow-lists for legacy codebases
- Fast single-pass analysis suitable for pre-commit hooks

## Installation
pip install resource-cleanup-auditor

## Usage
resource-cleanup-auditor .
resource-cleanup-auditor src/ --config .cleanuprc.toml --fail-on-high

## Architecture
Single-pass AST walker with symbol tracking. Reports are rendered via rich for terminal readability.