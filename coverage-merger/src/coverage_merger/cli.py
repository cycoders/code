import sys
import typer
from pathlib import Path
from rich.console import Console
from rich.traceback import install

from coverage_merger import __version__
from coverage_merger.merger import merge_reports, write_xml, compute_stats
from coverage_merger.visualizer import print_table, generate_html


install(show_locals=True)

app = typer.Typer(add_completion=False)
console = Console()


@app.command(no_args_is_help=True)
def merge(
    inputs: list[Path] = typer.Argument(
        ..., help="Input coverage XML files (e.g. cov1.xml cov2.xml)"
    ),
    output: Path = typer.Option("merged.xml", "-o", "--output", help="Output XML"),
    html: Optional[Path] = typer.Option(
        None, "-H", "--html", help="Path for HTML report"
    ),
    prev: Optional[Path] = typer.Option(
        None, "-p", "--prev", help="Baseline XML for delta analysis"
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
) -> None:
    """Merge coverage XML files from parallel pytest runs."""
    if not inputs:
        typer.echo("Error: At least one input XML required.", err=True)
        raise typer.Exit(1)

    if verbose:
        console.print(f"[cyan]coverage-merger v{__version__}[/] -- Merging {len(inputs)} reports")

    try:
        with console.status("[bold green]Parsing and merging reports..."):
            merged_data = merge_reports(inputs)
        write_xml(merged_data, output)
        console.print(f"[bold green]✓ Merged report: {output}")

        stats = compute_stats(merged_data)
        print_table(stats, prev)

        if html:
            generate_html(merged_data, html, prev)
            console.print(f"[bold green]✓ HTML report: {html}")

        if verbose:
            total_files = len(stats)
            avg_pct = sum(s["line_pct"] for s in stats) / total_files if total_files else 0
            console.print(f"[dim]Summary: {total_files} files, avg {avg_pct:.1f}% lines[/]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]", err=True)
        raise typer.Exit(1) from e


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", help="Show version", callback=lambda v: typer.echo(__version__) or typer.Exit()
    ),
) -> None:
    """CLI for merging pytest coverage XML reports."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


if __name__ == "__main__":
    app()
