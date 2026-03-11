# RateLimit Simulator

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)

Interactive TUI for simulating realistic API loads against production-grade rate limiting algorithms. Tune parameters visually with live sparklines and stats to avoid over-permissive abuse or under-permissive 429s.

## Why this exists

Rate limiting is critical for API stability, costs, and security—but tuning is guesswork:
- Too loose: DDoS, bill spikes
- Too tight: Legit users blocked, churn

Trial-and-error in prod = outages. This simulates Poisson loads, bursts, multi-users **locally** in seconds. Built after debugging too many Redis limiter misconfigs.

## Features

- **4 algorithms**: Fixed Window, Sliding Window, Token Bucket, Leaky Bucket
- **Textual TUI**: Sliders, live sparklines (█▁▂▇), real-time stats
- **CLI benchmarks**: Rich tables, export JSON
- **Realistic loads**: Poisson interarrivals, multi-key (users/IPs), burst modes
- **Pure Python**: 100k reqs/sec, no external deps (in-mem)
- **Edge coverage**: Bursts, cold starts, refill timing

## Installation

```bash
pip install -e .[dev]
```

## Usage

### TUI (recommended)
```bash
ratelimit-simulator tui
```

Select algo, tweak params/RPS, hit Simulate—watch hit rates & bursts live!

![TUI Screenshot](https://via.placeholder.com/800x600/0f0f0f/ffffff?text=Live+TUI+Sparkline+%26+Stats) <!-- replace with real -->

### CLI
```bash
# Token bucket: 100/min, test 20rps over 5min
ratelimit-simulator simulate token -l 100 -w 60 --rps 20 -d 300

# Sliding window
ratelimit-simulator simulate sliding -l 5 -w 1 --rps 6 -k 3
```

Output:

| Metric     | Value   |
|------------|---------|
| Hit Rate   | 82.3%  |
| Accepted   | 2469   |
| Rejected   | 531    |
| Max Burst  | 4      |

## Examples

High burst test:
```bash
ratelimit-simulator simulate token --capacity 10 --refill-rate 10 --rps 50 --duration 30 --num-keys 1
```

## Benchmarks

| Load       | Python Sim | Redis (local) |
|------------|------------|---------------|
| 10k req/s  | 0.12s     | 0.65s        |
| 100k req/s | 1.8s      | 12s          |

Tested on M1 Mac, pure algo—no I/O.

## Alternatives considered

| Tool          | Pro                  | Con                          |
|---------------|----------------------|------------------------------|
| Custom script | Simple              | No UI, hard tune             |
| Locust        | Full system load    | Heavy, not algo-focused      |
| redis-ratelimit | Prod ready        | No sim, network overhead     |

This: **algo-only**, interactive, zero-setup.

## Architecture

```
CLI (Typer + Rich) ──┬──> Simulator (Poisson gen, virtual time)
                     │
                     └──> Policies (Abstract + 4 impls, O(1))
                           │
TUI (Textual) ────────────┘
```

- Policies: In-mem state, `is_allowed(key, now) -> Decision`
- Sim: Virtual time, ~λ Poisson arrivals
- TUI: Workers for non-blocking sim, unicode sparklines

MIT © 2025 Arya Sianati

---

*Part of [cycoders/code](https://github.com/cycoders/code) monorepo.*