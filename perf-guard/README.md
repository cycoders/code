# Perf Guard

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)

**Detects performance regressions in scripts and CLI tools by statistically comparing runtimes against committed baselines.**

## Why this exists

Refactors often slow down your tools by 20%+. Perf Guard runs benchmarks (mean ± stddev), stores baselines in git, and fails fast if regressions exceed your threshold. 

Perfect for monorepos: guard CLIs, scripts, and binaries in CI.

*No profilers needed—just whole-process timing.*

## Features

- 🏃 Multiple iterations + warmup for stable stats
- 📊 Rich tables with mean/stddev/min/max/change %
- 🔍 Auto baseline names (SHA256 of command)
- 🚨 CI-ready: exit 1 on regression
- ⚡ Any executable (Python, Node, Go, shell, etc.)
- 💾 JSON baselines: `perf-guard baseline command...`

## Installation

```
cd perf-guard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quickstart

1. **Baseline** (commit the JSON!):
   ```bash
   perf-guard baseline --name quicksort python examples/sort.py 10000
   ```

2. **Check** (fails on regression):
   ```bash
   perf-guard check python examples/sort.py 10000  # auto-detects name
   ```

**Example output:**

| Metric  | Baseline | Current | Change |
|--------|----------|---------|--------|
| Mean   | 45.2ms  | **52.1ms** | **+15.3%** 🚨

## Benchmarks

| Iterations | Time |
|------------|------|
| 10         | 0.5s |
| 100        | 4s   |

Overhead: ~1ms/run.

## Examples

`examples/sort.py`: Bubble vs insertion sort demo.

```bash
perf-guard baseline python examples/sort.py bubble 10000
perf-guard baseline python examples/sort.py insertion 10000
perf-guard check python examples/sort.py bubble 10000
```

## CI Integration

```yaml
- name: Perf Guard
  run: |
    perf-guard check mycli --test-data
    # Fails if >10% slower
```

Commit `.perfguard-baselines/*.json`.

## Config

CLI flags:

```
perf-guard baseline [FLAGS] COMMAND...

  --iterations 10  # min 3
  --warmup     2
  --threshold  0.1  # 10%
  --timeout    60
  --name       auto # SHA256(command)[:12]
```

## Architecture

```
CLI (Typer + Rich) → Benchmark (subprocess + perf_counter)
                 ↓
              Stats (statistics.mean/stdev)
                 ↓
            Baselines (.perfguard-baselines/*.json)
```

Heuristic: Regression if `new_mean > old_mean * (1 + threshold)`.

## Alternatives considered

| Tool | Why not |
|------|---------|
| time | No stats/multirun |
| hyperfine | Shell-only, no git baselines |
| pytest-benchmark | Tests only |

Perf Guard: **Zero deps**, git-native, any lang.

## License

MIT © 2025 Arya Sianati