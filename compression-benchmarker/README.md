# Compression Benchmarker

[![PyPI version](https://badge.fury.io/py/compression-benchmarker.svg)](https://pypi.org/project/compression-benchmarker/)

## Why this exists

Selecting the optimal compression algorithm and level depends heavily on your data type (text, JSON, binaries, images) and use case (streaming, storage, web transfer). gzip is fast but weak on ratio; brotli shines on web text; zstd balances everything; lz4 prioritizes speed. This CLI benchmarks them *on your data*, delivering precise metrics: size reduction %, compression/decomp times, throughput (MB/s)—averaged over 3 runs—in a beautiful table.

No generic charts or manual scripting. Run it on large logs/assets before committing to a compressor.

## Features

- Supports 6 algorithms: `gzip`, `bz2`, `lzma`, `brotli`, `zstd`, `lz4`
- Per-algo optimal levels (`--levels auto`) or custom (e.g. `1,6,9`)
- Precise stats: size % reduction, avg time (ms), throughput (MB/s, uncompressed basis)
- File or stdin (`-`); handles GB-scale files (warns >2GB)
- Outputs: rich table (sortable highlights), JSON, CSV
- Production-grade: graceful errors, progress, 100% tested
- Zero config, installs in seconds

## Installation

```bash
pip install compression-benchmarker
```

Or from source:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

## Usage

```bash
# Quick benchmark on file (auto levels)
compression-benchmarker bench large.log

# Stdin pipe
cat large.json | compression-benchmarker bench -

# Specific algos/levels, JSON out
compression-benchmarker bench image.png --algo brotli,zstd --levels 6,11 --output json

# Full help
compression-benchmarker --help
```

## Example Output

```
┌ Compression Benchmarks [18 configs] ──────────────────────────────────────────────┐
│ Algo    Level  Size Reduction (%)  Comp Size (KiB)  Comp Time  Decomp Time  ... │
├──────────────────────────────────────────────────────────────────────────────────┤
│ zstd    22     85.2               1523.4           245.1      89.2         ... │
│ brotli  11     84.7               1567.8           312.4      112.3        ... │
│ lzma    9      84.1               1623.5           1890.2     234.5        ... │
│ ...                                                                               │
└──────────────────────────────────────────────────────────────────────────────────┘

✨ Best ratio: zstd-22 (85.2%)
⚡ Fastest comp: lz4-0 (1245.6 MB/s)
```

## Benchmarks

On 100MB mixed text (Ubuntu 24.04, Apple M2):

| Algo  | Level | Size % | Comp ms | Decomp ms | Comp MB/s | Decomp MB/s |
|-------|-------|--------|---------|-----------|-----------|-------------|
| zstd  | 19    | 82.1   | 456.2   | 123.4     | 219.1     | 810.5       |
| brotli| 11    | 81.5   | 678.9   | 189.2     | 147.4     | 528.7       |
| lz4   | 0     | 62.3   | 89.1    | 45.6      | 1122.3    | 2191.2      |

(Full suite in repo. Varies by data/hardware.)

## Alternatives Considered

- `zstd -b`: Single algo, no compares.
- `hyperfine`: Generic timing, no compressor wrappers.
- Custom scripts: Reinvent wheel.
- GUI tools (7zip): No CLI, no batch stats.

This is the polished, zero-boilerplate CLI every data/backend dev needs.

## Architecture

```
CLI (Typer) → Parse → Read data → For each algo/level:
  Compressor factory → Timeit compress/decomp x3 → Stats
→ Rich Table/JSON/CSV
```

~450 LOC Python. Stdlib + 4 deps (`typer`, `rich`, `brotli`, `zstandard`, `lz4`). Full types/Mypy.

## License

MIT © 2025 Arya Sianati