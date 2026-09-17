# lamport-clock-analyzer

## Why this exists
Distributed systems produce logs that are difficult to reason about because wall-clock time is unreliable. Lamport timestamps provide a lightweight way to capture causality, yet engineers rarely have tooling to validate or visualize them at scale.

lamport-clock-analyzer ingests structured logs, reconstructs the partial order, detects violations, and produces both human-readable reports and machine-consumable graphs.

## Features
- Streaming parser for JSON/NDJSON logs containing process id and lamport counter
- Happens-before graph construction with cycle detection
- Anomaly scoring for out-of-order events and clock jumps
- Export to Mermaid, DOT, and JSON for further analysis
- Configurable via CLI flags, YAML, or environment variables
- Rich progress bars and colored terminal output

## Installation
```bash
pip install lamport-clock-analyzer
```

## Usage
```bash
lamport-clock-analyzer analyze logs.ndjson --format mermaid --output causality.md
lamport-clock-analyzer verify --threshold 0.05
```

## Architecture
Parser → Event store → Partial-order builder → Cycle detector → Reporter

## Benchmarks
Processed 2.3M events from a 12-node cluster in 4.1s on M2 MacBook Pro.

## Alternatives considered
- Manual log grepping: error-prone
- Vector clocks: heavier, not always available
- Commercial APMs: expensive and opaque