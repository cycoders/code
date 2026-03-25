import typer
import logging
from pathlib import Path
from typing import List, Optional, Dict

from rich.console import Console
from rich.table import Table
from rich.progress import track

import json

import httpx
from datetime import datetime

from http_cache_analyzer import __version__

from .models import HttpResponse
from .har_parser import load_har_entries
from .live_fetcher import fetch_url
from .scorer import score_policy
from .simulator import simulate_sequence, simulate_burst


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

app = typer.Typer(add_completion=False)


@app.command(help="Analyze cache policies from HAR or live URL")
def analyze(
    har: Optional[Path] = typer.Argument(None, help="HAR file path"),
    live: Optional[str] = typer.Option(None, "--live", help="Live URL"),
    header: List[str] = typer.Option([], "--header", help="Extra header: name=value"),
    output: str = typer.Option("table", "--output/-o", help="table|json|csv"),
):
    responses: List[HttpResponse] = []

    extra_headers: Dict[str, str] = {}
    for h in header:
        if '=' in h:
            k, v = h.split('=', 1)
            extra_headers[k] = v

    if har:
        with console.status("[bold blue]Parsing HAR..."):
            responses = load_har_entries(har)
    elif live:
        console.print(f"[bold blue]Fetching [cyan]{live}[/]...")
        try:
            resp = fetch_url(live, extra_headers)
            responses = [resp]
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
    else:
        typer.echo("Specify --live URL or HAR file", err=True)
        raise typer.Exit(1)

    if not responses:
        typer.echo("No responses to analyze", err=True)
        raise typer.Exit(1)

    results = []
    for resp in track(responses, description="Scoring..."):
        score, sugg = score_policy(resp.cache_policy, str(resp.url))
        result = {
            "url": str(resp.url),
            "status_code": resp.status_code,
            "max_age": resp.cache_policy.max_age,
            "score": score,
            "suggestion": sugg,
            "cache_control": resp.headers.get('cache-control', ''),
            "etag": resp.cache_policy.etag,
        }
        results.append(result)

    if output == "table":
        table = Table(title="HTTP Cache Analysis", show_header=True, header_style="bold magenta")
        table.add_column("URL", style="cyan", no_wrap=False)
        table.add_column("Status", justify="right")
        table.add_column("Max-Age", justify="right")
        table.add_column("Score", justify="right", style="bold green")
        table.add_column("Suggestion")

        for r in results:
            url_short = str(r["url"])[:60] + "..." if len(str(r["url"])) > 60 else str(r["url"])
            table.add_row(
                url_short,
                str(r["status_code"]),
                str(r["max_age"]) if r["max_age"] else "None",
                f"{r['score']}/100",
                r["suggestion"],
            )
        console.print(table)

    elif output == "json":
        console.print(json.dumps(results, indent=2))
    elif output == "csv":
        import csv
        import sys
        writer = csv.DictWriter(sys.stdout, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    else:
        typer.echo(f"Unknown output: {output}", err=True)
        raise typer.Exit(1)


@app.command(help="Simulate cache hit rates")
def simulate(
    har: Path = typer.Argument(..., help="HAR file"),
    burst_size: int = typer.Option(1000, "--burst", "-b", help="Burst sim requests"),
):
    responses = load_har_entries(har)
    console.print(f"[bold blue]Loaded {len(responses)} responses[/]")

    # Sequence sim
    seq = simulate_sequence(responses)
    console.print(f"[bold green]Sequence hit rate: {seq['hit_rate']:.1f}% (" f"{seq['hits']}/{seq['total']})[/]")

    # Burst sim
    burst = simulate_burst(responses, burst_size)
    console.print(f"[bold green]Burst ({burst_size}) hit rate: {burst['hit_rate']:.1f}% (" f"{burst['hits']}/{burst['total']})[/]")


@app.command()
def version():
    console.print(f"http-cache-analyzer v{__version__}")


if __name__ == "__main__":
    app()
