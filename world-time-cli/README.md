# World Time CLI

A polished CLI tool to display current local times across multiple timezones in a beautiful Rich-powered terminal table. Perfect for remote teams coordinating across the globe.

## Why?

Switching between browser tabs or apps to check times in different zones wastes time. This tool gives you an instant, colorful overview right in your terminal.

## Installation

In the monorepo:

```bash
cd world-time-cli
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --help
```

### Examples

**Default popular timezones:**

```bash
python src/main.py
```

**Specific timezones:**

```bash
python src/main.py --tz "America/New_York" "Europe/Paris" "Asia/Singapore"
```

**Search timezones:**

```bash
python src/main.py --search "Tokyo"
```

**List all (pipe to less):**

```bash
python src/main.py --list | less
```

## Features

- Rich tables: timezone, offset, time, date
- Fuzzy search for quick discovery
- Defaults to common timezones (NY, LA, London, Berlin, Tokyo, Sydney)
- Handles invalid timezones gracefully
- Cross-platform: Linux & macOS (Python 3.9+)

## Testing

```bash
pip install pytest
pytest
```

## License

MIT