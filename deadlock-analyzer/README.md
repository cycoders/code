# deadlock-analyzer

## Why this exists
Multithreaded Python code is notoriously hard to reason about. Subtle lock ordering mistakes cause deadlocks that only manifest under load or specific scheduling. This tool performs fast static analysis to surface potential deadlock cycles before they reach production.

## Features
- AST-based extraction of Lock/RLock acquisition patterns
- Builds a directed lock-order graph across functions and modules
- Cycle detection with clear path reporting
- Handles common context-manager and acquire/release idioms
- Zero runtime overhead; pure static analysis

## Installation
```bash
pip install deadlock-analyzer
```

## Usage
```bash
python -m deadlock_analyzer src/
```

## Architecture
See docs/architecture.md for the graph construction and cycle-finding algorithm.

## Alternatives considered
- Runtime tools (detect deadlocks only when they occur)
- Thread sanitizer (heavy, language-specific)
- Manual code review (does not scale)
