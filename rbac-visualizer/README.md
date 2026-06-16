# rbac-visualizer

## Why this exists
RBAC misconfigurations are a leading cause of breaches in Kubernetes and internal platforms. Existing tools either dump YAML or require manual inspection. rbac-visualizer renders policies as directed graphs, highlights risky permission combinations, and detects drift between desired and actual state.

## Features
- Parse ClusterRole/Role/RoleBinding/ServiceAccount from live clusters or YAML
- Build permission graph with subject-role-resource edges
- Detect privilege escalation paths and wildcard risks
- Export Graphviz DOT, Mermaid, or interactive HTML
- CI-friendly JSON report with severity scoring
- Supports aggregated ClusterRoles and impersonation rules

## Installation
```bash
pip install rbac-visualizer
```

## Usage
```bash
# Live cluster
rbac-visualizer --context prod --output html > report.html

# From manifests
rbac-visualizer --manifests ./k8s/rbac/ --format mermaid
```

## Architecture
Single-pass parser using kubernetes Python client + lightweight graph model. All analysis is local; no data leaves the machine.

## Benchmarks
- 1200 RBAC objects: <800ms on M2 Mac
- Memory: <45 MiB

## Alternatives considered
- kubectl auth can-i (per-user, no overview)
- rbac-lookup (text only)
- Popeye (static analysis, no graphs)
