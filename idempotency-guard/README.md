# idempotency-guard

## Why this exists
Retrying HTTP or RPC calls without proper idempotency handling causes duplicate charges, duplicate records, and corrupted state. This library provides a battle-tested, configurable guard that stores idempotency keys with TTLs, detects replays, and supports multiple backends.

## Features
- Key generation, storage, and validation in one API
- Pluggable backends (memory, redis, sqlite)
- Automatic expiration and cleanup
- Configurable retention windows and collision policies
- CLI for local testing and debugging
- Full type hints and structured logging

## Installation
pip install idempotency-guard

## Usage
```python
from idempotency_guard import IdempotencyGuard, RedisBackend

guard = IdempotencyGuard(backend=RedisBackend(url="redis://localhost"))
if guard.is_duplicate("payment-123", window=3600):
    return guard.get_cached_result("payment-123")
result = process_payment()
guard.store("payment-123", result, ttl=86400)
```

## Benchmarks
Memory backend: 12µs per check
Redis backend: 1.2ms per check (local)

## Alternatives considered
- Custom Redis SETNX scripts: too low-level and error-prone
- Stripe-style idempotency: vendor specific
- Database unique constraints: no TTL or replay payload support