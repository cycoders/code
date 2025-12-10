# Crypto Portfolio CLI

A fast CLI for checking live cryptocurrency prices and valuing portfolios in the terminal, powered by [CoinGecko's free API](https://www.coingecko.com/en/api).

## Why?

Crypto never sleeps. Skip browsers and apps—get prices or portfolio totals in ~150ms with beautiful tables. Ideal for developers, traders, and long-term holders.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --help
```

### Check Prices

```bash
python src/main.py price --coins bitcoin,ethereum,solana --currency usd
```

| Coin     | Price (USD) |
|----------|-------------|
| Bitcoin  | 60,000.5000 |
| Ethereum | 3,000.2500  |
| Solana   | 150.7500    |

### Track Portfolio

```bash
python src/main.py portfolio --holdings "bitcoin:0.2,ethereum:5,solana:150" --currency eur
```

| Coin     | Amount   | Price (EUR) | Value (EUR) |
|----------|----------|-------------|-------------|
| Bitcoin  | 0.200000 | 55,000.0000 | 11,000.0000 |
| Ethereum | 5.000000 | 2,750.0000  | 13,750.0000 |
| Solana   | 150.000000 | 138.0000 | 20,700.0000 |
| **TOTAL** |          |             | **45,450.0000 EUR** |

## Features

- 10k+ coins, 150+ currencies
- Custom portfolios
- Rich tables, error handling
- No API keys or auth

## Performance

- API: 100-200ms
- Local: negligible

Tested on Linux/macOS.

## License

MIT