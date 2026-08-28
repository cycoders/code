# config-consistency-checker

## Why this exists
Configuration drift silently breaks deployments. This tool parses multiple environment configs, performs semantic comparison, enforces organizational policies, and produces clear reports.

## Features
- Supports YAML, TOML, JSON, .env
- Semantic diff ignoring formatting/whitespace
- Policy rules (required keys, value types, regex patterns)
- CI-friendly exit codes and SARIF output
- Beautiful rich tables and diff rendering

## Installation
pip install config-consistency-checker

## Usage
config-consistency-checker check prod.yaml staging.yaml --policy policy.yaml
