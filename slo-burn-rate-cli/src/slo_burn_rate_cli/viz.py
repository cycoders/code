from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich import box
import pandas as pd
from typing import Dict, Any


def render_results(
    results: Dict[str, Any],
    output: str,
    console: Console,
) -> None:
    """Render results as table or JSON."""
    if output == 'json':
        print(results['history_df'].tail(100).round(4).to_json(orient='records', date_format='iso'))
        return

    # Summary table
    table = Table(title="[bold cyan]SLO Burn Rate Summary[/]", box=box.ROUNDED, show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    burn_emoji = "✅" if results['current_burn_rate'] <= 1 else "⚠️"
    table.add_row("Current SLO", f"{results['current_slo']:.4f}")
    table.add_row("Burn Rate (28d)", f"{results['current_burn_rate']:.1%} {burn_emoji}")
    table.add_row("Budget Remaining", f"{results['budget_remaining_pct']:.1%}")
    if results['forecast_exhaust_date']:
        table.add_row("Forecast Exhaust", results['forecast_exhaust_date'].strftime('%Y-%m-%d %H:%M'))
    else:
        table.add_row("Forecast Exhaust", "Never 🥳")

    console.print(table)

    # History bar chart (last 24 points)
    history = results['history_df'].tail(24)
    if not history.empty:
        console.print("\n[bold green]Burn Rate History (last 24h hourly):[/]")
        max_rate = history['burn_rate'].max()
        bar_width = 50
        for _, row in history.iterrows():
            rate = row['burn_rate']
            bar_len = int((rate / max_rate) * bar_width) if max_rate > 0 else 0
            bar = "█" * bar_len + "░" * (bar_width - bar_len)
            label = "[green]" if rate <= 1 else "[red]"
            console.print(f"{row['date'].strftime('%H:%M')} | {bar} {label}{rate:.1%}[/{label}]")
