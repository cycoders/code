# CLI Benchmarker

[![PyPI version](https://badge.fury.io/py/cli-benchmarker.svg)](https://pypi.org/project/cli-benchmarker/) [![Tests](https://github.com/cycoders/code/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/cycoders/code/actions/workflows/ci.yml)

## Why this exists

Optimizing CLI tools, build scripts, and shell workflows is crucial for developer productivity. Tools like `hyperfine` excel at wall-clock timing but ignore CPU utilization and memory footprint—key bottlenecks in real-world scenarios like `npm install`, `docker build`, or custom scripts. **CLI Benchmarker** delivers **holistic metrics** with rigorous statistics (mean ± std, median, P95), failure tolerance, timeouts, and publication-quality terminal output using Rich. Track regressions across git commits and export JSON for dashboards.

Built for senior engineers who demand precision without complexity.

## Features

- 🏃 **Multi-command comparison**: Benchmark `cmd1` vs `cmd2` side-by-side
- ⏱️ **Wall time** + **CPU time** (user/sys/children) + **peak RSS memory**
- 📊 **Statistics**: mean, std dev, median, P95, min/max + distribution sparklines
- 🚀 **Warmup runs** to stabilize caches/JIT
- 🛡️ **Timeouts** & failure reporting (exit codes, verbose stdout/stderr)
- 🎨 **Rich tables** & progress bars
- 📤 **JSON export** for CI/parsing
- 🔄 **Cross-platform** (Linux/macOS/Windows via psutil)

## Benchmarks vs Alternatives

| Feature          | CLI Benchmarker | hyperfine | /usr/bin/time |
|------------------|-----------------|-----------|---------------|
| Wall time        | ✅              | ✅        | ✅            |
| CPU time         | ✅              | ❌        | Partial      |
| Peak memory      | ✅              | ❌        | ❌            |
| P95/Stats        | ✅ Full         | Basic    | ❌            |
| Sparklines/Viz   | ✅ Rich         | Basic    | ❌            |
| Multi-cmd        | ✅              | ✅        | ❌            |
| JSON export      | ✅              | ❌        | ❌            |

Example on `npm ci` (30 runs, M2 Mac):

```
┌─────────────┬──────┬──────────┬───┬──────────┬──────┬──────┬──────────────┬──────┬────────────┐
│ Command     │ Runs │   Mean   │ ± │  Median  │  P95 │ Min  │ Max [spark]  │ CPU  │    Mem     │
├─────────────┼──────┼──────────┼───┼──────────┼──────┼──────┼──────────────┼──────┼────────────┤
│ npm ci      │ 30/30│ 2450ms   │67 │ 2432ms   │ 2601 │ 2356 │ 2678 [▁▂▄▄▅▅▆▇█]│ 1.8s │ 245.2/312MB│
└─────────────┴──────┴──────────┴───┴──────────┴──────┴──────┴──────────────┴──────┴────────────┘
```

## Installation

```
pip install cli-benchmarker
```

Or from source:

```
git clone https://github.com/cycoders/code
cd cli-benchmarker
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"
```

## Usage

### Single command

```bash
cli-benchmarker run "npm run build"
```

### Compare commands

```bash
cli-benchmarker run "docker build ." "docker build . --no-cache"
```

### Advanced

```bash
cli-benchmarker run "git status" \
  --warmup 5 --runs 50 --timeout 2.0 --json results.json --verbose
```

Full help:

```bash
cli-benchmarker run --help
```

**Pro tip**: Alias `cb=cli-benchmarker run` and pipe to `tee` for records.

## Examples

See `examples/` for `npm`/`docker`/`rustc` workflows.

## Architecture

```
CLI (Typer)
  ↓
Benchmarker (subprocess + psutil sampling)
  ↓
Metrics: {wall_time, cpu_total, mem_peak, success}
  ↓
Stats (statistics.stdlib) + Sparklines
  ↓
Rich Table (console)
```

- Sampling thread for real-time peak memory (20ms poll)
- Handles timeouts/kills gracefully
- Only successful runs in stats (failed noted)

## Alternatives considered

| Tool       | Why not? |
|------------|----------|
| hyperfine  | No CPU/mem/stats depth |
| time(1)    | No viz/repeat/stats |
| custom bash| Reinvent wheel, error-prone |

CLI Benchmarker is 100% Python stdlib + minimal deps, zero config.

## Development

```
pytest
ruff check .
ruff format .
```

## License

MIT © 2025 Arya Sianati

---

⭐ Love it? [Star the monorepo](https://github.com/cycoders/code)!