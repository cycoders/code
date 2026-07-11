# config-hot-reloader

## Why this exists
Long-running services often need configuration changes without restarts. Existing solutions either poll too aggressively, lack atomic updates, or crash on invalid config. config-hot-reloader provides a minimal, production-grade primitive for watching and safely applying config changes.

## Features
- File-system event driven watching (no polling)
- Atomic swap with validation hooks
- Automatic rollback on validation or application errors
- Thread-safe accessors with context manager support
- Support for YAML, JSON, TOML
- Rich logging and optional Prometheus metrics

## Installation
```bash
pip install config-hot-reloader
```

## Usage
```python
from config_hot_reloader import ConfigReloader

def validate(cfg):
    assert 'port' in cfg

reloader = ConfigReloader('config.yaml', validator=validate)
with reloader:
    app.run(port=reloader.current['port'])
```

## Architecture
Uses watchdog observers + a small state machine. All updates happen under a reader-writer lock. Validation failures never affect the live config.

## Benchmarks
Reload latency < 8 ms on typical config sizes. Memory overhead < 200 KiB.

## Alternatives considered
- watchdog + manual reload: no safety guarantees
- dynaconf: heavier, polling based
- pydantic-settings: no hot reload