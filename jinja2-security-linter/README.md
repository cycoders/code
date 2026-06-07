# jinja2-security-linter

## Why this exists
Jinja2 templates are a common source of subtle security vulnerabilities and maintenance issues in Python web applications. Existing linters focus on syntax or style; none provide deep, context-aware analysis of injection risks, dangerous filter usage, or auto-escaping violations.

jinja2-security-linter fills this gap with a fast, production-grade static analyzer that senior engineers can run in CI or locally with zero configuration.

## Features
- Precise Jinja2 AST analysis (no regex hacks)
- Detects XSS, SQLi via templates, unsafe |safe usage, and missing autoescape
- Context-aware rules that understand include/extends and macro definitions
- Actionable fixes with --fix
- Rich terminal output and SARIF/JSON export for CI
- Extensible rule system

## Installation
```bash
pip install jinja2-security-linter
```

## Usage
```bash
jinja2-security-linter templates/
jinja2-security-linter app/templates --fix --format sarif
```

## Architecture
Uses the official jinja2 parser to build an AST, then runs a visitor-based rule engine. All rules are pure functions with no side effects.

## Benchmarks
Scans 50k lines of real templates in <800ms on a laptop.

## Alternatives considered
- Semgrep (too generic, noisy)
- Bandit (no Jinja2 template support)
- Custom ruff plugin (insufficient AST depth for templates)