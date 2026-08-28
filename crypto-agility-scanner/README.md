# crypto-agility-scanner

## Why this exists
Cryptographic standards evolve. Hard-coded algorithms (MD5, SHA1, AES-ECB, RSA-1024) and pinned primitive choices create long-term technical debt and compliance risk. Existing linters focus on secrets or CVEs; none systematically surface algorithmic rigidity across a codebase and provide actionable migration guidance.

## Features
- Language-aware parsing for Python, JavaScript/TypeScript, Go, Java
- Detects direct algorithm literals, import aliases, and common wrapper patterns
- Severity classification (critical/weak/legacy/acceptable)
- Concrete replacement suggestions with library versions
- SARIF + JSON output for CI integration
- Configurable allow/deny lists and baseline support
- Graceful handling of minified and generated files

## Installation
```bash
pip install crypto-agility-scanner
```

## Usage
```bash
crypto-agility-scanner scan src/ --format sarif --output report.sarif
crypto-agility-scanner scan . --baseline .crypto-baseline.json --fail-on critical
```

## Architecture
Tree-sitter parsers feed a small rule engine. Each rule emits structured findings with confidence, location, and migration metadata. Results are aggregated and rendered by rich formatters.

## Benchmarks
Scanned 420k LOC monorepo in 4.8s on M2 Mac. False-positive rate <2% on internal corpus.

## Alternatives considered
- semgrep crypto rules (too noisy, no migration hints)
- bandit (secret-focused, limited algorithm coverage)
- custom regex (brittle on modern syntax)