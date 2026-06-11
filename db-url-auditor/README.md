# db-url-auditor

## Why this exists
Database connection strings are a frequent source of security incidents and operational failures. Hard-coded credentials, missing TLS requirements, and provider-specific misconfigurations often slip into production. db-url-auditor provides fast, accurate static analysis of connection URLs with actionable remediation.

## Features
- Strict parsing of 12+ database schemes (PostgreSQL, MySQL, MongoDB, Redis, etc.)
- Detection of cleartext credentials, weak TLS settings, and missing SSL modes
- Provider-specific rule engine with 40+ checks
- Human-readable and JSON output modes
- Exit codes suitable for CI pipelines

## Installation
```bash
pip install db-url-auditor
```

## Usage
```bash
db-url-auditor "postgresql://user:pass@localhost:5432/db?sslmode=disable"
```

## Architecture
Parser normalizes URLs into a typed model. Auditor applies a registry of rule functions that emit structured findings. Rules are versioned and easily extended.

## Alternatives considered
- urlparse + manual checks: too error-prone
- existing linters: lack provider depth and CI-friendly output
