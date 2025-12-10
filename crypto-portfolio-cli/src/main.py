import os
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent))

import argparse
from rich.console import Console
from rich.table import Table
import api
import portfolio
import utils

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description='Crypto Portfolio CLI - Live prices & portfolio tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py price --coins bitcoin,eth --currency usd
  python src/main.py portfolio --holdings 'btc:1,eth:10' --currency usd
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands', required=True)

    price_parser = subparsers.add_parser('price', help='Fetch coin prices')
    price_parser.add_argument('--coins', required=True, help='Comma-separated coin IDs (bitcoin,ethereum)')
    price_parser.add_argument('--currency', default='usd', help='Fiat currency (default: usd)')

    portfolio_parser = subparsers.add_parser('portfolio', help='Compute portfolio value')
    portfolio_parser.add_argument('--holdings', required=True, help='coin:amount,coin:amount (bitcoin:0.1,eth:2.5)')
    portfolio_parser.add_argument('--currency', default='usd', help='Fiat currency (default: usd)')

    args = parser.parse_args()

    try:
        if args.command == 'price':
            coins = [c.strip().lower() for c in args.coins.split(',')]
            prices = api.get_prices(coins, args.currency)
            table = Table(title=f'Crypto Prices ({args.currency.upper()})')
            table.add_column('Coin', style='cyan')
            table.add_column(f'Price ({args.currency.upper()})', justify='right', style='green')
            for coin, price in prices.items():
                table.add_row(coin.title(), f'{price:,.4f}')
            console.print(table)

        elif args.command == 'portfolio':
            holdings = utils.parse_holdings(args.holdings)
            coins = list(holdings)
            prices = api.get_prices(coins, args.currency)
            table = Table(title=f'Portfolio ({args.currency.upper()})')
            table.add_column('Coin', style='cyan')
            table.add_column('Amount', justify='right')
            table.add_column(f'Price ({args.currency.upper()})', justify='right', style='green')
            table.add_column(f'Value ({args.currency.upper()})', justify='right', style='magenta')
            total = 0.0
            for coin in coins:
                amount = holdings[coin]
                price = prices.get(coin, 0.0)
                value = amount * price
                amt_str = f'{amount:.6f}'.rstrip('0').rstrip('.') if amount % 1 else f'{int(amount)}'
                table.add_row(coin.title(), amt_str, f'{price:,.4f}', f'{value:,.4f}')
                total += value
            table.add_row('[bold]TOTAL[/bold]', '', '', f'[bold green]{total:,.4f}[/bold green]')
            console.print(table)
    except Exception as e:
        console.print(f'[red]Error: {str(e)}[/red]')
        sys.exit(1)

if __name__ == '__main__':
    main()
