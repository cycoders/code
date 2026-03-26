# Domain Profiler CLI

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Why this exists

When evaluating a website, API endpoint, or third-party service, developers need a quick, privacy-respecting way to gather key intelligence: ownership (WHOIS), infrastructure (DNS/SSL/headers), technology stack, and security posture. Online tools leak data to third parties; manual checks are tedious. This CLI aggregates 10+ checks into a beautiful report in <2s, with JSON export and configurable caching.

Built for senior engineers tired of tab-switching between dig, whois, ssllabs.com, wappalyzer, and securityheaders.com.

## Features

- **DNS**: A/AAAA/MX/NS/CNAME/TXT/SOA records
- **WHOIS**: Registrar, dates, nameservers, contacts
- **SSL/TLS**: Cert details, expiry, subject/issuer (chain preview)
- **HTTP Headers**: Full table with security-relevant highlights
- **Tech Stack**: Fingerprint server, frameworks, CMS (React, Nginx, PHP, WordPress +50 patterns, confidence scores)
- **Security Score**: 0-100 audit (HSTS, CSP, XFO, expiry, etc.) with fixes
- Parallel execution, rich progress/UI, caching (1h TTL), JSON/YAML/CLI output
- Graceful offline/timeout handling, no paid APIs

## Benchmarks

| Domain | Time |
|--------|------|
| google.com | 1.2s |
| github.com | 1.5s |
| internal (failures) | 0.8s |

Tested on M1 Mac/i7 Linux (parallel IO-bound).

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Full profile
python -m domain_profiler_cli.cli example.com

# JSON output
python -m domain_profiler_cli.cli example.com --json

# Skip sections
python -m domain_profiler_cli.cli example.com --no-ssl --no-whois

# Custom port/HTTP
python -m domain_profiler_cli.cli example.com --port 8443 --http

# Help
python -m domain_profiler_cli.cli --help
```

**Example Output:**

Rich panels/tables with progress spinner.

## Configuration

`~/.domain-profiler-cli/config.toml`:

```toml
[core]
timeout = 10
user_agent = "DomainProfiler/0.1.0"
cache_ttl_hours = 1

[security]
warn_threshold = 70
```

## Architecture

- Modular profilers (dns.py, ssl.py, etc.) return dicts
- `profile_domain()` orchestrates with ThreadPoolExecutor
- Rich Console for output (Panels, Tables, Progress)
- TOML config + JSON cache (pathlib)

## Alternatives Considered

- **Online**: SecurityHeaders.com, Wappalyzer (privacy/API limits)
- **Scripts**: Custom dig/whois/curl (no aggregation/UI)
- **Full suites**: Aquatone/Nuclei (overkill/offsec-focused)

This is lightweight (zero bloat), offline-capable, dev-centric.

## Development

```bash
pip install -r requirements.txt
pytest
```

## License

MIT © 2025 Arya Sianati