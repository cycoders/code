# sbom-diff-cli

## Why this exists
Software supply chains evolve rapidly. When a new SBOM is generated after a build or dependency update, teams need an immediate, precise diff that highlights security-relevant changes rather than raw JSON noise.

sbom-diff-cli produces human-readable, machine-actionable diffs between CycloneDX or SPDX SBOMs, annotating each change with known vulnerability severity and policy violations.

## Features
- Supports CycloneDX 1.4+ and SPDX 2.3/3.0
- Severity-aware change classification using OSV.dev data
- Policy gate support via simple YAML rules (fail on new criticals, license changes, etc.)
- Rich terminal output with tables, JSON, SARIF, and GitHub Actions annotations
- Streaming mode for CI pipelines handling multi-gigabyte SBOMs
- Deterministic output for reproducible builds

## Installation
```bash
pip install sbom-diff-cli
```

## Usage
```bash
sbom-diff-cli diff old.sbom.json new.sbom.json --format sarif --fail-on critical
sbom-diff-cli policy-check sbom.json --rules policy.yaml
```

## Architecture
Thin CLI layer over a streaming parser that builds two in-memory component graphs, computes a symmetric difference, then enriches results with vulnerability lookups. Zero network calls unless --fetch-vulns is passed.

## Benchmarks
Diffing 50k-component SBOMs completes in <800ms on M2 MacBook Pro.

## Alternatives considered
- manual jq scripts: error-prone and lack vulnerability context
- existing SBOM tools: focus on generation, not precise diffing with policy
