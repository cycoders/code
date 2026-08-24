# copyleft-risk-analyzer

## Why this exists
Copyleft licenses (GPL, AGPL, MPL, EPL) impose strong obligations that many organizations discover only after shipping. Existing license checkers report SPDX identifiers but do not model obligation propagation across transitive dependencies or produce engineering-ready reports.

copyleft-risk-analyzer builds the full dependency graph, classifies licenses, calculates obligation scope, and outputs a machine-readable risk report plus a human summary.

## Features
- Supports Python, Node, Go, Rust, and Java ecosystems via lockfile + SBOM ingestion
- Recursive obligation propagation with accurate scope (library vs binary vs network)
- Risk scoring: critical (AGPL in prod), high, medium, low
- SARIF + JSON + Markdown output for CI integration
- Policy file support for allowed/denied licenses and exceptions
- Zero network calls after initial metadata fetch; fully offline capable

## Installation
```bash
pip install copyleft-risk-analyzer
```

## Usage
```bash
copyleft-risk-analyzer scan --lockfile poetry.lock --format sarif > report.sarif
copyleft-risk-analyzer scan --sbom sbom.json --policy policy.yaml
```

## Architecture
- `graph.py`: builds unified dependency graph
- `license_db.py`: curated SPDX + obligation matrix
- `propagator.py`: walks graph applying obligation rules
- `reporter.py`: renders SARIF/JSON/Markdown

## Benchmarks
Scans 1200-dependency monorepo in <800 ms on M2 Mac.

## Alternatives considered
- FOSSology: heavy, requires database
- Licensee: only detects project license, no transitive analysis
- ClearlyDefined: excellent data but no local policy engine