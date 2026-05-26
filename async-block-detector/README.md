# async-block-detector

## Why this exists
Async Python code is fragile: a single `time.sleep`, `requests.get`, or `open(...).read()` inside an async function silently destroys concurrency. This tool statically detects such calls, explains the risk, and suggests replacements.

## Features
- AST-based detection of 40+ common blocking primitives
- Understands `asyncio`, `trio`, and `anyio`
- Configurable allow/deny lists via pyproject.toml
- Beautiful rich terminal output with fix suggestions
- 100% type-checked, zero runtime dependencies for the core

## Installation
```bash
pip install async-block-detector
```

## Usage
```bash
python -m async_block_detector src/
```

## Architecture
Thin CLI wrapper around a pure-Python AST visitor. No runtime monkey-patching.

## Alternatives considered
- `flake8-async` (limited rules)
- `pylint` async extensions (too noisy)
- `mypy` plugins (type-system only)

MIT licensed.