# flamegraph-diff-cli

## Why this exists
Performance regressions hide in hot paths. Comparing raw numbers or single flamegraphs is slow and error-prone. This tool ingests multiple folded stack files, aligns symbols, computes per-frame delta and statistical significance, and emits a concise, color-coded report plus an interactive HTML diff.

## Features
- Parses Brendan Gregg folded stacks and pprof protobuf
- Symbol normalization across builds (demangling, inlining)
- Mann-Whitney U test per frame with configurable α
- Rich terminal report + self-contained HTML diff with zoom
- CI-friendly exit codes and JUnit XML
- Zero external services, pure Python + optional Rust accel

## Installation
pip install flamegraph-diff-cli

## Usage
flamegraph-diff-cli before.folded after.folded --alpha 0.01 --format html > diff.html

## Architecture
Parser → SymbolTable → FrameAligner → StatsEngine → Renderers

## Alternatives considered
- manual diff in spreadsheet: too slow
- speedscope: no regression stats
- benchstat: only scalar metrics