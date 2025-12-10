# Public Holidays CLI

A polished CLI tool to fetch and display public holidays for any country and year using the free [Nager.Date API](https://date.nager.at/) (no auth required). Perfect for travel planning, scheduling across timezones, or HR tools—delivers instant, richly formatted tables.

## Why?
Quickly check non-working days globally without browsers or bloated apps. Built for developers: minimal deps, fast, cross-platform (Linux/macOS).

## Installation
```bash
python3 -m venv venv
source venv/bin/activate  # or . venv/bin/activate on macOS
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py --help

# List all supported countries
python src/main.py countries

# Holidays for a country (code or full name)
python src/main.py holidays --country US --year 2024
python src/main.py holidays --country "United Kingdom" --year 2025
```

### Example Output (holidays US 2024):
```
╒══════════════════════════════════════════════════════════════╕
│ Holidays in US (2024)                                        │
╞══════════════════════════════════════════════════════════════╡
│ 2024-01-01 │ New Year's Day                          │ New Year's Day │ True  │ False │
│ 2024-07-04 │ Independence Day                        │ Independence Day │ True  │ False │
│ ...                                                           │
╘══════════════════════════════════════════════════════════════╛
```

## Performance
API latency: ~50-200ms. Local ops negligible.

## Tests
```bash
pip install pytest requests-mock  # dev deps
pytest
```

MIT © 2025 Arya Sianati