# context-manager-linter

## Why this exists
Python's context managers (`with` statements) are the idiomatic way to manage resources such as files, locks, sockets, and database connections. Forgetting them leads to resource leaks, deadlocks, and hard-to-debug production issues. Existing linters catch only a narrow set of cases. context-manager-linter performs deep AST + semantic analysis to find missing context managers across an entire codebase.

## Features
- Detects direct calls to resource constructors used outside `with`
- Understands common stdlib and third-party resources (file, Lock, sqlite3, requests.Session, etc.)
- Configurable allow-list and custom resource definitions
- Rich terminal output with code snippets and fix suggestions
- Fast: only parses Python files, respects .gitignore
- Exit code 1 on findings for CI integration

## Installation
```bash
pip install context-manager-linter
```

## Usage
```bash
context-manager-linter .
context-manager-linter src/ --config .cmlint.toml
```

## Architecture
Uses `ast` + `libcst` for precise source mapping, a small registry of known resources, and a lightweight dataflow pass to track bare constructor calls.

## Benchmarks
Scans CPython's 1.2 M LOC in <4 s on a laptop.

## Alternatives considered
pylint (limited rules), flake8-contextlib (too narrow), semgrep (requires writing rules).