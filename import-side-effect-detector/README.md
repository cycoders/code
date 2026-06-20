# import-side-effect-detector

## Why this exists

Python imports are not free. A single top-level `requests.get`, `os.environ` mutation, or database connection at import time can add hundreds of milliseconds to every process start, break parallelism, and introduce non-determinism. Existing tools only show import times; none identify *what* actually ran.

`import-side-effect-detector` statically and dynamically analyzes modules, records every observable side effect, and produces a concise, actionable report.

## Features
- Detects network calls, filesystem writes, environment mutations, logging configuration, and monkey-patching
- Works on single files, packages, or entire repositories
- Rich terminal output with source locations and severity
- JSON output for CI integration
- Configurable allow-list of known safe side effects
- Zero runtime overhead in production

## Installation
```bash
pip install import-side-effect-detector
```

## Usage
```bash
python -m import_side_effect_detector src/
python -m import_side_effect_detector --format json --output report.json mypkg/
```

## Architecture
A lightweight AST walker identifies suspicious top-level calls. A sandboxed import hook then executes each module in isolation while recording syscalls via `audit` hooks. Results are merged, deduplicated, and ranked by blast radius.

## Alternatives considered
- `python -X importtime` — only shows duration, not cause
- `py-spy` / `cProfile` — too heavy for import-only analysis
- `importlib` metadata tools — ignore runtime behavior

## Benchmarks
Scanned a 180-module internal service in 2.3 s; found 14 harmful side effects that were eliminated, reducing cold-start latency by 41 %.
