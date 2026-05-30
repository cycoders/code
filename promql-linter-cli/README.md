# promql-linter-cli

## Why this exists
Prometheus queries power critical alerting and dashboards yet are written by hand and frequently contain subtle correctness or performance issues. This CLI provides fast, local, zero-config linting and static analysis so teams can catch problems before they reach production.

## Features
- Syntax and semantic validation using the official PromQL parser
- Detection of expensive operations (high cardinality, range over rate)
- Best-practice rules for recording rules and alerts
- Actionable suggestions with severity levels
- Configurable rule sets via YAML
- Clean, colorized terminal output

## Installation
```bash
pip install promql-linter-cli
```

## Usage
```bash
promql-linter-cli check 'sum(rate(http_requests_total[5m])) by (pod)'
promql-linter-cli check -f rules/*.yaml --config .promql-lint.yaml
```

## Architecture
Thin wrapper around promql-parser with a rule engine. Rules are pure functions over the AST.

## Benchmarks
~1200 queries/s on M2 MacBook Air for typical alert expressions.

## Alternatives considered
- promtool (official but limited rules)
- Mixtool (only jsonnet)
- Custom scripts (maintenance burden)