# orm-nplus1-detector

## Why this exists
N+1 queries silently destroy database performance in ORM-heavy codebases. Manual detection is tedious and error-prone. This tool provides fast, reliable static + dynamic analysis with precise remediation guidance.

## Features
- Hybrid static AST + runtime SQL tracing
- Support for SQLAlchemy, Django ORM, Peewee
- Actionable suggestions with exact code locations
- HTML/terminal reports with query counts
- CI-friendly exit codes and JSON output

## Installation
pip install orm-nplus1-detector

## Usage
python -m orm_nplus1_detector scan ./src
python -m orm_nplus1_detector trace --app myapp --duration 30s

## Architecture
Lightweight plugin system for ORM adapters. Core engine uses AST visitors and SQL comment annotations for correlation.

## Alternatives considered
pylint plugins (too noisy), django-debug-toolbar (runtime only), manual EXPLAIN analysis (slow).