# accept-header-resolver

## Why this exists
HTTP content negotiation via the Accept header is notoriously error-prone. Most implementations ignore q-values, fail on wildcards, or produce non-deterministic results. This library provides a complete, spec-compliant resolver that senior engineers can trust in APIs, proxies and SDKs.

## Features
- Full RFC 9110 parsing including q, charset and level parameters
- Deterministic precedence rules with stable tie-breaking
- Support for media ranges, subtypes and type wildcards
- CLI for quick debugging and testing
- Zero dependencies, pure Python, fully typed

## Installation
```bash
pip install accept-header-resolver
```

## Usage
```python
from accept_header_resolver import resolve
best = resolve('text/html,application/xhtml+xml;q=0.9,*/*;q=0.8', ['text/html', 'application/json'])
```

## CLI
```bash
python -m accept_header_resolver 'text/*;q=0.5,application/json' 'application/json text/plain'
```

## Benchmarks
Resolves 10k headers in <12 ms on CPython 3.12 (see tests/bench.py).

## Alternatives considered
- werkzeug's parse_accept_header: incomplete wildcard handling
- Python's email.message: not designed for media types