# Pokemon Info CLI

A lightweight, zero-dependency (runtime) CLI tool to fetch detailed Pokémon information from the public PokeAPI (https://pokeapi.co).

## Features

- Fetch Pokémon by name (e.g., 'pikachu') or National Dex ID (e.g., '25')
- Nicely formatted output with ID, height, weight, types, and base stats
- Optional JSON output (`--json`)
- Optional sprite URL (`--sprite`)
- Handles errors gracefully (e.g., invalid Pokémon)
- Uses only Python stdlib for requests and parsing

## Installation

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --help
```

### Examples

```bash
# Formatted info
python src/main.py pikachu
```

Sample output:
```
#025 Pikachu
Height: 0.4 m (4 dm)
Weight: 6.0 kg (60 hg)
Types: Electric

Base Stats:
  Hp           : 35
  Attack       : 55
  Defense      : 40
  Special-Attack: 50
  Special-Defense: 50
  Speed        : 90

Sprite: https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png
```

```bash
# JSON output
python src/main.py 25 --json

# With sprite
python src/main.py charizard --sprite
```

## Testing

```bash
pytest -q
```

All tests pass (unit tests for parsing and CLI args; no network required).

## License

MIT
