# test-data-synthesizer

## Why this exists
Generating production-like test data is painful. Manual fixtures drift, random data violates schemas, and existing tools lack statistical control or reproducibility guarantees. This CLI produces deterministic, schema-valid, statistically realistic datasets from JSON Schema, SQL DDL or example CSV files.

## Features
- Schema inference from JSON Schema, CREATE TABLE statements or CSV samples
- Configurable distributions (normal, zipf, weighted categorical)
- Foreign-key aware relational data generation
- Reproducible runs via seed + manifest
- Streaming output for multi-GB datasets
- Built-in PII avoidance patterns

## Installation
```bash
pip install test-data-synthesizer
```

## Usage
```bash
# From JSON Schema
test-data-synthesizer generate --schema user.json --rows 100000 --out users.parquet

# From SQL DDL with relations
test-data-synthesizer generate --ddl schema.sql --relations relations.yaml --seed 42
```

## Architecture
Core pipeline: SchemaParser → ConstraintGraph → DistributionSampler → RowEmitter. All randomness is sourced from a seeded numpy Generator. Relational integrity is enforced via topological sort and foreign-key backfill.

## Benchmarks
Generating 1M rows with 12 columns and 3 FKs: 3.8s (Apple M2, Python 3.12). 40× faster than faker with constraints.

## Alternatives considered
- faker: no schema validation or distributions
- synth: closed source
- dbgen: limited to TPC-H schemas
