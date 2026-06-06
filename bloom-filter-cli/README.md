# bloom-filter-cli

## Why this exists
Bloom filters are ubiquitous in high-scale systems for deduplication, cache-break avoidance, and set membership. Choosing m (bits) and k (hash functions) is error-prone and directly impacts memory and false-positive rates. This tool removes the guesswork with mathematically sound calculations, Monte-Carlo simulation, and ready-to-use configuration snippets.

## Features
- Optimal parameter calculation from expected n and target fp rate
- Monte-Carlo simulation with multiple hash families
- Export to Redis, Cassandra, or custom bit-array formats
- Streaming cardinality estimator from real data
- Production config validation and migration helpers

## Installation
```bash
pip install bloom-filter-cli
```

## Usage
```bash
bloom-filter-cli size --elements 100_000_000 --fp 0.001
bloom-filter-cli simulate --config config.yaml --stream data.jsonl
```

## Benchmarks
Single-core simulation of 10M elements completes in <800 ms. Results match theoretical predictions within 0.2%.

## Alternatives considered
- hand-rolled spreadsheets (error-prone)
- online calculators (no simulation, no export)
- language-specific libs (no cross-system config)