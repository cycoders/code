# migration-safety-analyzer

## Why this exists
Production database migrations are the highest-risk change engineers make. A single `ALTER TABLE` can acquire exclusive locks for minutes, cause replication lag, or silently truncate data. Existing linters only check syntax. This tool performs deep static analysis of migration scripts against a target schema to surface data-loss, locking, and performance hazards.

## Features
- Detects destructive operations (DROP COLUMN, TRUNCATE, type changes that lose precision)
- Estimates worst-case lock duration using dialect-specific rules
- Flags missing `WHERE` clauses on large tables
- Produces a risk score and suggested safer rewrite
- Supports PostgreSQL, MySQL, and SQLite
- Works from plain SQL files or Alembic migrations

## Installation
```bash
pip install migration-safety-analyzer
```

## Usage
```bash
migration-safety-analyzer analyze migrations/ --schema current.sql --dialect postgres
```

## Architecture
Parser → Risk Rules Engine → Dialect Cost Model → Reporter. All rules are pure functions with no side effects.

## Alternatives considered
- `pg-safe-migrate`: only Postgres, no risk scoring
- `sqitch` verify: runtime only
- Manual review: inconsistent

## Benchmarks
Analyzes 1200-line migration in <80 ms on M2 Mac.