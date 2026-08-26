# memfrag-profiler

## Why this exists
Long-running Python services suffer silent memory bloat from fragmentation that standard profilers miss. memfrag-profiler attaches to live processes, classifies arena usage, and produces actionable allocation advice.

## Features
- Non-intrusive attachment via ptrace or signal
- Arena and block-level fragmentation metrics
- Interactive terminal visualization
- Export to JSON/CSV for CI
- Heuristic recommendations for gc and allocator tuning

## Installation
pip install memfrag-profiler

## Usage
memfrag-profiler attach --pid 1234 --duration 30s

## Architecture
Core logic in src/memfrag_profiler/analyzer.py uses pymalloc internals knowledge. CLI built with typer + rich.

## Benchmarks
Typical overhead <3% CPU on 8GB heap.

## Alternatives considered
Valgrind massif (heavy), tracemalloc (no fragmentation view).