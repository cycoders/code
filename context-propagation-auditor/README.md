# context-propagation-auditor

## Why this exists
Context variables are essential for distributed tracing, request IDs, deadlines and auth in modern Python services. Missing propagation across asyncio.create_task, ThreadPoolExecutor, or subprocess boundaries silently breaks observability and correctness.

## Features
- Static AST analysis for asyncio, concurrent.futures and contextvars usage
- Detects create_task, submit, and map calls missing context copying
- Reports exact line numbers and suggested fixes
- Supports custom context keys via config
- Fast, zero-runtime-overhead analysis

## Installation
pip install -e .

## Usage
context-propagation-auditor src/

## Architecture
Uses libcst for precise, comment-preserving transforms and a small rule engine for patterns.

## Alternatives considered
- pylint/extensions: too generic
- manual grep: error-prone

MIT licensed.