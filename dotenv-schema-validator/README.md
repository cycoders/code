# dotenv-schema-validator

## Why this exists
Misconfigured environment variables cause a disproportionate number of production incidents. This tool brings schema-driven validation to .env files with the same rigor used for API payloads.

## Features
- JSON Schema draft-2020-12 support
- Type coercion and strict mode
- Custom rule extensions via Python callables
- Clear error reporting with line numbers
- CI-friendly exit codes and JUnit XML output

## Installation
pip install dotenv-schema-validator

## Usage
```bash
dotenv-schema-validator validate --schema schema.json .env
```