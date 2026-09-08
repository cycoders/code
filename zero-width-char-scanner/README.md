# zero-width-char-scanner

## Why this exists
Zero-width characters and other invisible Unicode code points are increasingly used in supply-chain attacks to hide malicious code or create visually identical but semantically different identifiers. Manual review is impossible at scale.

## Features
- Fast streaming scan of any directory tree
- Detects 12 categories of dangerous invisible characters
- Configurable allow-list per file extension
- SARIF and JSON output for CI integration
- Colorized terminal report with exact byte offsets
- Respects .gitignore by default

## Installation
```bash
pip install zero-width-char-scanner
```

## Usage
```bash
zero-width-char-scanner .
zero-width-char-scanner --format sarif src/ > report.sarif
```

## Architecture
Single-pass UTF-8 streaming scanner built on the unicodedata and regex modules. No external data files.

## Benchmarks
Scans 50k LOC Python repository in <120 ms on M2 Mac.

## Alternatives considered
- grep with Unicode properties (too slow, no categories)
- ripgrep with custom patterns (no structured reporting)
