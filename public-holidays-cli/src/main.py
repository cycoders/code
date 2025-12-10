import argparse
import os
import sys

from rich.console import Console
from rich.table import Table

from holidays import get_available_countries, get_holidays, get_country_code


def main():
    parser = argparse.ArgumentParser(
        description="Public Holidays CLI: Fetch holidays by country/year using Nager.Date API"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Countries subcommand
    countries_parser = subparsers.add_parser(
        "countries", help="List all supported countries"
    )

    # Holidays subcommand
    holidays_parser = subparsers.add_parser("holidays", help="List holidays for a country")
    holidays_parser.add_argument(
        "--year", type=int, default=2024, help="Year to fetch holidays for (default: 2024)"
    )
    holidays_parser.add_argument(
        "--country",
        required=True,
        help="Country code (e.g., 'US') or full name (e.g., 'United States')",
    )

    args = parser.parse_args()

    # Prepend src/ to path for imports
    sys.path.insert(0, os.path.dirname(__file__))

    console = Console()

    try:
        if args.command == "countries":
            countries = get_available_countries()
            table = Table(title="Available Countries")
            table.add_column("Code", style="cyan")
            table.add_column("Name")
            for country in sorted(countries, key=lambda c: c["name"]):
                table.add_row(country["countryCode"], country["name"])
            console.print(table)

        elif args.command == "holidays":
            country_code = get_country_code(args.country)
            holidays_list = get_holidays(args.year, country_code)
            table = Table(title=f"Public Holidays in {country_code} ({args.year})")
            table.add_column("Date", style="magenta")
            table.add_column("Local Name")
            table.add_column("Name")
            table.add_column("Fixed", justify="center")
            table.add_column("Global", justify="center")
            for holiday in sorted(holidays_list, key=lambda h: h["date"]):
                table.add_row(
                    holiday["date"],
                    holiday["localName"],
                    holiday["name"],
                    str(holiday["fixed"]),
                    str(holiday["global"]),
                )
            console.print(table)

    except KeyboardInterrupt:
        console.print("\n[red]Interrupted.[/red]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    main()