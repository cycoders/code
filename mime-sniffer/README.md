# mime-sniffer

## Why this exists
Incorrect Content-Type headers enable XSS, bypass upload filters, and break caching. Existing tools either rely solely on extensions or require heavy native dependencies. mime-sniffer delivers fast, dependency-light, production-grade detection using magic bytes plus lightweight structural heuristics.

## Features
- 40+ built-in signatures for common web, document, and archive formats
- Heuristic fallback for JSON, CSV, XML, and SVG
- Streaming analysis (no full file load for large inputs)
- Exit codes suitable for CI
- Human and machine-readable output

## Installation
```bash
pip install mime-sniffer
```

## Usage
```bash
mime-sniffer report.pdf
mime-sniffer --json suspicious.exe | jq .
```

## Architecture
Single-pass magic matching followed by optional content parsers. All signatures are defined in a single declarative table for easy extension.

## Alternatives considered
- python-magic: heavy libmagic dependency
- filetype: limited signature set and no heuristics
- file(1): not embeddable in Python tooling

## Benchmarks
Average 0.8 ms per 10 MB file on M2 Mac (stddev < 0.1 ms).