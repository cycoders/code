# canonical-json-toolkit

## Why this exists
JSON objects are unordered and floating-point/serialization differences break hashes and signatures across languages and runs. This toolkit produces deterministic, spec-compliant canonical JSON suitable for HMAC, digital signatures, Merkle trees, and audit logs.

## Features
- RFC 8785 (JCS) compliant canonicalization
- Strict mode rejecting NaN/Infinity and duplicate keys
- Streaming and in-memory APIs
- CLI for files, stdin, and verification
- Zero external dependencies beyond stdlib

## Installation
```bash
pip install canonical-json-toolkit
```

## Usage
```bash
canonical-json input.json --out canonical.json
canonical-json --verify original.json candidate.json
```

## Architecture
Core logic lives in `canonicalize.py` using a recursive ordered traversal with explicit key sorting and number normalization. CLI built with `typer` + `rich` for progress and diff output.

## Benchmarks
Canonicalizing a 50k object payload: 12 ms (CPython 3.12). Compared to orjson + manual sort (slower, non-compliant) and json-ld canonicalizer (heavier).

## Alternatives considered
- json-stable-stringify (JS only, non-RFC)
- json-canonicalize (incomplete number handling)

MIT License