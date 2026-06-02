# systemd-unit-builder

## Why this exists
Deploying services to Linux often involves writing brittle systemd units by hand. This tool produces correct, hardened, and maintainable units from a small declarative YAML file while catching common misconfigurations before deployment.

## Features
- Declarative YAML schema with full validation
- Automatic dependency ordering and After= resolution
- Security hardening (PrivateTmp, NoNewPrivileges, SystemCallFilter, etc.)
- Environment variable templating and file inclusion
- Resource limits, restart policies, and socket activation support
- Dry-run and diff output for safe iteration

## Installation
pip install systemd-unit-builder

## Usage
systemd-unit-builder --config api.yaml --out api.service

## Architecture
Parser → Validator → Hardener → Renderer. All stages are independently testable.