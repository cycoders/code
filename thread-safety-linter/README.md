# Thread Safety Linter

## Why this exists
Concurrent Python code is notoriously difficult to get right. Subtle races, forgotten locks, and unsafe shared-state patterns frequently slip into production, causing intermittent failures that are expensive to debug.

Thread Safety Linter provides fast, local, zero-dependency static analysis that catches the most common classes of thread-safety mistakes before they reach CI.

## Features
- Detects unprotected access to mutable objects across threads
- Identifies lock ordering violations and potential deadlocks
- Reports missing or inconsistently used locks around critical sections
- Understands threading primitives, concurrent.futures, and queue usage
- Beautiful rich terminal output with fix suggestions
- Configurable via pyproject.toml or CLI flags

## Installation
```bash
pip install thread-safety-linter
```

## Usage
```bash
thread-safety-linter .
thread-safety-linter src/ --fail-on high --format json
```

## Architecture
The tool parses AST, builds a lightweight dataflow graph of thread interactions, and applies a set of targeted rules. It deliberately avoids full symbolic execution for speed while still catching the majority of real-world bugs senior engineers care about.

## Alternatives considered
- pylint concurrency plugins (too noisy)
- bandit (security-focused, misses data races)
- Custom mypy plugins (require type annotations we cannot assume)

MIT licensed and ready for monorepo adoption.