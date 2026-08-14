# graphql-cost-analyzer

## Why this exists
Production GraphQL APIs frequently suffer from expensive nested queries that bypass rate limits and exhaust database connections. This tool statically analyzes query documents against a schema to compute a deterministic cost score and highlight risky patterns.

## Features
- Accurate cost calculation using field weights and list multipliers
- Detection of n+1, deep nesting, and cyclic fragment risks
- Support for custom cost directives and schema extensions
- Beautiful CLI output with color-coded risk levels
- Batch analysis of .graphql files with JSON export

## Installation
```bash
pip install graphql-cost-analyzer
```

## Usage
```bash
graphql-cost-analyzer analyze schema.graphql query.graphql
graphql-cost-analyzer analyze --max-depth 7 --export json results/
```

## Architecture
The analyzer builds a cost-weighted AST using graphql-core, applies configurable multipliers for lists and fragments, and walks the document once. All heuristics are deterministic and require no network calls.

## Alternatives considered
- graphql-depth-limit (runtime only)
- Apollo Studio (paid, SaaS)
- Custom in-house scripts (brittle)

## Benchmarks
Analyzes 500-line queries in <40 ms on a laptop CPU.