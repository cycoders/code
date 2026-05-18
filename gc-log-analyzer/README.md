# gc-log-analyzer

## Why this exists
Production services frequently suffer from mysterious latency spikes or OOM kills because GC tuning remains an opaque, trial-and-error process. gc-log-analyzer turns verbose GC logs into concise, actionable intelligence.

## Features
- Parses both HotSpot unified logging and CPython gc module output
- Detects allocation rate spikes, promotion failures, and long pauses
- Recommends concrete flag changes with estimated impact
- Exports interactive HTML reports and CSV for dashboards
- Zero external dependencies beyond the Python standard library

## Installation
```bash
pip install gc-log-analyzer
```

## Usage
```bash
python -m gc_log_analyzer gc.log --format html --out report.html
```

## Architecture
A streaming line parser feeds a state machine that tracks generations and pause durations. Recommendations are produced by a small rule engine with conservative defaults.

## Alternatives considered
- GCViewer: GUI only, no CLI or recommendations
- jcmd GC.class_stats: lower level, no cross-runtime support