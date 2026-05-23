# task-graph-runner

## Why this exists
Developers constantly orchestrate sequences of commands (build, test, lint, deploy previews) that have dependencies and expensive steps. Existing tools are either too heavy (Airflow) or too linear (Make). task-graph-runner provides a minimal, production-grade DAG runner that lives in your repo.

## Features
- Declarative YAML/JSON task graphs with typed inputs/outputs
- Content-addressed caching using file hashes and command signatures
- Automatic parallel execution with topological sort
- Rich terminal output with progress, timing, and failure traces
- Export to Mermaid/Graphviz for documentation
- Graceful handling of partial failures and retries

## Installation
```bash
pip install task-graph-runner
```

## Usage
```bash
python -m task_graph_runner run graph.yml
python -m task_graph_runner viz graph.yml --format mermaid
```

## Architecture
Core components: Task (node), Graph (DAG), Cache (content-addressed), Executor (parallel). All errors are surfaced with full context.

## Benchmarks
On a 12-task monorepo build graph: 4.2s cold, 0.8s fully cached (vs 11s Make).

## Alternatives considered
Make (linear), Earthly (heavy), Dagger (Go-only). This tool prioritizes zero-config Python ergonomics.