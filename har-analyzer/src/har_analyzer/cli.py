import typer
import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.traceback import install

from .analyzer import compute_stats, top_slow, domains, resource_types, detect_anomalies
from .renderer import render_stats, render_waterfall, render_domains, render_types, render_anomalies


install(show_locals=True)

app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Analyze a HAR file for performance insights.")
def analyze(
    har_file: Path = typer.Argument(..., help="Path to HAR file"),
    json_output: Optional[Path] = typer.Option(None, "--json", help="Output JSON report"),
):
    """Analyze HAR file and print insights."""
    if not har_file.exists():
        typer.echo(f"❌ File not found: {har_file}", err=True)
        raise typer.Exit(1)

    try:
        with open(har_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"❌ Invalid JSON in HAR: {e}", err=True)
        raise typer.Exit(1)

    if "log" not in data:
        typer.echo("❌ Invalid HAR: missing 'log' key", err=True)
        raise typer.Exit(1)

    log = data["log"]
    if "entries" not in log:
        console.print("[yellow]No entries found in HAR.[/yellow]")
        raise typer.Exit(0)

    entries = log["entries"]

    # Compute metrics
    stats = compute_stats(entries)
    slow = top_slow(entries)
    doms = domains(entries)
    types_r = resource_types(entries)
    anomalies = detect_anomalies(entries)

    # JSON output first if requested
    if json_output:
        report = {
            "stats": stats,
            "top_slow": [summarize_entry(e) for e in slow],
            "domains": dict(doms),
            "resource_types": dict(types_r),
            "anomalies": anomalies,
        }
        with open(json_output, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"📊 JSON report saved: {json_output}")

    # Terminal render
    console.print("\n" + "="*80)
    console.print("[bold blue]HAR Analyzer v0.1.0[/bold blue]")
    console.print("="*80 + "\n")

    render_stats(stats)
    render_waterfall(slow[:20])  # Top 20 for brevity
    render_domains(doms)
    render_types(types_r)
    if anomalies:
        render_anomalies(anomalies)
    else:
        console.print("[green]✅ No major anomalies detected![/green]")


def summarize_entry(e: dict) -> dict:
    """Minimal entry summary for JSON."""
    req = e.get("request", {})
    resp = e.get("response", {})
    return {
        "url": req.get("url", ""),
        "method": req.get("method", ""),
        "status": resp.get("status"),
        "time": e.get("time"),
        "size": resp.get("bodySize"),
    }


if __name__ == "__main__":
    app()