#!/usr/bin/env python3
'''World Time CLI main entrypoint.'''

import argparse
from datetime import datetime, timezone

from rich import box
from rich.console import Console
from rich.table import Table

from src.timezone_manager import (
    DEFAULT_TZS,
    get_all_timezones,
    get_current_time,
    search_timezones,
)

console = Console()

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display current times in multiple timezones.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --tz "America/New_York" "Europe/Paris"
  %(prog)s --search "Berlin"
  %(prog)s --list | less
        """.strip(),
    )
    parser.add_argument(
        "--tz",
        nargs="*",
        metavar="TZ",
        default=DEFAULT_TZS,
        help="Specific timezones (default: popular ones)",
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search for timezones containing the string",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available timezones",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    utc_now = datetime.now(timezone.utc)

    if args.list:
        tzs = get_all_timezones()
        for tz in tzs:
            console.print(tz)
        return

    if args.search:
        tzs = search_timezones(args.search)
        if not tzs:
            console.print("[red]No matching timezones found.[/red]")
            return
        table = Table(
            title=f"Timezones matching '{args.search}'",
            show_header=False,
            box=None,
        )
        table.add_column("Timezone", style="cyan")
        for tz in tzs[:50]:
            table.add_row(tz)
        console.print(table)
        if len(tzs) > 50:
            console.print(f"[dim]... and {len(tzs) - 50} more[/dim]")
        return

    # Display times
    times = []
    for tz_name in args.tz:
        try:
            time_info = get_current_time(tz_name, utc_now)
            times.append(time_info)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    if not times:
        console.print("[yellow]No valid timezones provided.[/yellow]")
        return

    table = Table(title="World Clock", box=box.ROUNDED)
    table.add_column("Timezone", style="magenta")
    table.add_column("Offset", style="green")
    table.add_column("Local Time", justify="right", style="blue")
    table.add_column("Date", style="white")
    for t in times:
        table.add_row(t["name"], t["offset"], t["time"], t["date"])
    console.print(table)


if __name__ == "__main__":
    main()