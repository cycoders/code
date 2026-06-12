# lease-guard

## Why this exists
Distributed systems require reliable lease management to coordinate access to shared resources. Incorrect handling leads to split-brain, data corruption, or stalled progress. lease-guard provides a production-grade implementation with automatic renewal, fencing tokens, and deterministic release semantics.

## Features
- Automatic lease renewal with jittered backoff
- Fencing token generation and validation
- Safe release that prevents use-after-release
- Configurable TTL, renewal window, and max skew
- Thread-safe and async-compatible facade
- Rich CLI for local simulation and debugging

## Installation
```bash
pip install lease-guard
```

## Usage
```python
from lease_guard import LeaseClient
client = LeaseClient(redis_url="redis://...")
lease = client.acquire("resource/key", ttl=30)
# use resource with lease.token
lease.release()
```

## Architecture
Core logic in src/lease_guard/lease.py uses monotonic time, token versioning, and state machine. CLI uses typer + rich. Tests cover renewal races, clock skew, and fencing violations.

## Benchmarks
Renewal overhead < 0.4 ms (p99). 50k acquire/release cycles in < 3 s on commodity hardware.

## Alternatives considered
etcd leases, consul sessions, Zookeeper ephemeral nodes — all require running external systems. lease-guard works with any backend via small adapter and runs fully offline for testing.