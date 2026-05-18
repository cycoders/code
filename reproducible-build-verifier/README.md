# reproducible-build-verifier

## Why this exists
Non-reproducible builds undermine supply-chain security, complicate caching, and erode trust in CI pipelines. This tool performs deep differential analysis between two build artifacts or manifests to surface timestamps, embedded paths, user IDs, locale settings, and other sources of nondeterminism.

## Features
- Manifest diffing with semantic understanding of common build outputs
- Detection of 20+ known nondeterminism patterns
- Beautiful rich-powered terminal reports with remediation hints
- Support for tar, zip, directory trees and custom JSON manifests
- Configurable allow-list for expected variation
- Exit codes suitable for CI gating

## Installation
```bash
pip install reproducible-build-verifier
```

## Usage
```bash
reproducible-build-verifier compare ./build1 ./build2
reproducible-build-verifier compare --manifest build1.json build2.json --format json
```

## Architecture
Core analysis pipeline: unpack → normalize metadata → semantic diff → pattern matching → reporting.

## Benchmarks
Typical 200 MiB artifact comparison completes in <800 ms on modern hardware.

## Alternatives considered
- diffoscope (too heavy, UI-focused)
- reprotest (coarse-grained, container-only)
- custom shell scripts (brittle, no semantic understanding)