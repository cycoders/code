# slsa-attestation-verifier

## Why this exists
Software supply chain attacks are rising. SLSA attestations provide cryptographic proof of build provenance, yet verifying them and enforcing meaningful policy remains tedious and error-prone. This tool makes verification a first-class, automatable step in any CI/CD pipeline.

## Features
- Verify SLSA v0.2/v1.0 attestations against artifact digests
- Enforce policy rules (builder ID, source URI, build time window)
- Support for in-toto+json and DSSE envelope formats
- Local file, OCI registry, and Sigstore integration
- Human-readable and machine-parsable (JSON) output
- Graceful handling of missing or malformed attestations

## Installation
```bash
pip install slsa-attestation-verifier
```

## Usage
```bash
# Verify a single artifact
slsa-attestation-verifier verify \
  --attestation build.attestation.json \
  --artifact dist/app.tar.gz

# Enforce policy from config
slsa-attestation-verifier verify \
  --config .slsa-policy.yaml \
  --artifact oci://ghcr.io/org/app@sha256:...
```

## Architecture
Thin CLI wrapper around in-toto and sigstore-python with a small, pure-Python policy engine. All heavy cryptographic work is delegated to well-audited libraries.

## Alternatives considered
- slsa-verifier (Go): excellent but requires Go toolchain and lacks Python-native policy hooks
- cosign: broader scope, heavier dependency tree

## Benchmarks
Verification of a 2 MiB attestation + artifact completes in <120 ms on a 2023 MacBook Pro (M2).
