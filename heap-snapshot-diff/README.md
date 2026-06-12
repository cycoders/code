# heap-snapshot-diff

## Why this exists
Memory leaks in long-running Python services are notoriously hard to catch before they impact production. Existing tools either require live attachment or produce opaque aggregate numbers. heap-snapshot-diff lets you capture two heap snapshots (e.g., before/after a deploy or load test) and produces a human-readable, machine-actionable diff that pinpoints exactly which object types grew, by how much, and where they were allocated.

## Features
- Parse tracemalloc, meliae, and py-spy heap dumps
- Object-level growth attribution with source location
- Configurable filters and significance thresholds
- Rich terminal tables, JSON, and SVG flamegraph output
- CI-friendly exit codes for regression gating

## Installation
```bash
pip install heap-snapshot-diff
```

## Usage
```bash
# Capture snapshots
python -X tracemalloc=25 app.py
python -m heap_snapshot_diff diff before.json after.json --min-growth 5%
```

## Architecture
Three-stage pipeline: parser → analyzer → reporter. All stages are independently testable and stream large snapshots without loading everything into RAM.

## Benchmarks
On a 120 MB snapshot pair: 1.8 s parse, 420 ms diff, <80 MB peak RSS.

## Alternatives considered
- objgraph: live-process only
- memory_profiler: line-level, not snapshot diff
- fil: excellent but requires LD_PRELOAD
