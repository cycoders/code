# graceful-shutdown

## Why this exists
Production services frequently lose in-flight work or leak resources during termination. This library provides a single, correct primitive for coordinating OS signals, draining concurrent work, enforcing hard deadlines, and emitting structured lifecycle telemetry.

## Features
- Signal coalescing (SIGTERM/SIGINT/SIGHUP)
- Task draining with bounded concurrency
- Deadline propagation and forced cancellation
- Structured JSON lifecycle events
- Zero-dependency core, optional rich logging
- Works with asyncio, threading, and sync servers

## Installation
pip install graceful-shutdown

## Usage
```python
from graceful_shutdown import ShutdownManager

mgr = ShutdownManager()
with mgr:
    # your server loop
    pass
```

## Architecture
Single coordinator object wrapping signal handlers, a cancellation scope, and a task registry. See docs/architecture.md.

## Benchmarks
Shutdown latency p99 < 12ms on 5000 tasks (see benchmarks/).

## Alternatives considered
- systemd notify: OS-specific
- anyio: too low-level
- django graceful: framework-specific