# raft-consensus-simulator

## Why this exists
Understanding Raft is essential for building reliable distributed systems, yet most engineers only encounter the paper once. This simulator provides an interactive, deterministic environment to explore leader election, log replication, and safety properties with full observability.

## Features
- Deterministic simulation of Raft with configurable node counts and network partitions
- Step-by-step execution with rich terminal visualization of state, logs, and votes
- Scenario replay from JSON definitions for regression testing of consensus edge cases
- Safety invariant checks (election safety, log matching, leader completeness)
- Exportable traces for further analysis

## Installation
```bash
pip install raft-consensus-simulator
```

## Usage
```bash
raft-consensus-simulator run --nodes 5 --scenario election
raft-consensus-simulator replay scenarios/partition.json
```

## Architecture
Core engine in pure Python using an event loop with explicit time advancement. Nodes are state machines; network is a controllable message bus.

## Benchmarks
Single simulation of 5-node cluster with 1000 log entries completes in <200ms on M2 MacBook.

## Alternatives considered
etcd raft tests (language-specific), Jepsen (heavyweight), and simple Python state machine examples (no visualization).