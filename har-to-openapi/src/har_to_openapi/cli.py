import typer
from pathlib import Path
from typing import List, Optional
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from .parser import parse_har_files
from .generator import generate_openapi, group_endpoints
from .utils import calculate_stats

app = typer.Typer()
console = Console()

@app.command()
def main(
    har_files: List[Path] = typer.Argument(..., exists=True, help="HAR files to process"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output OpenAPI YAML file"),
    preview: bool = typer.Option(False, "--preview", help="Show endpoint preview table"),
    merge: bool = typer.Option(True, "--merge", help="Merge endpoints across files"),
    min_samples: int = typer.Option(2, "--min-samples", help="Minimum samples per endpoint"),
):
    """Convert HAR files to OpenAPI 3.1 spec."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_parse = progress.add_task("[cyan]Parsing HARs...", total=len(har_files))
            all_entries = []
            for har_file in har_files:
                entries = parse_har(har_file)
                all_entries.extend(entries)
                progress.advance(task_parse)

            progress.add_task("[green]Grouping & inferring...", total=1)
            endpoints = group_endpoints(all_entries, min_samples=min_samples)
            progress.advance(task_parse)

        spec = generate_openapi(endpoints)

        if preview:
            show_preview(endpoints)

        stats = calculate_stats(endpoints, len(all_entries))
        console.print(stats)

        if output:
            output.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
            console.print(f"[bold green]✓ OpenAPI spec saved to {output}")
        else:
            console.print("[bold yellow]OpenAPI spec:")
            console.print(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True))

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}")
        raise typer.Exit(1)


def show_preview(endpoints: dict) -> None:
    table = Table(title="Inferred Endpoints")
    table.add_column("Path", style="cyan")
    table.add_column("Method", style="magenta")
    table.add_column("Samples", justify="right")
    table.add_column("Statuses", justify="right")
    table.add_column("Avg Time (ms)", justify="right")
    for path, ops in endpoints.items():
        for method, data in ops.items():
            samples = len(data["samples"])
            statuses = "/".join(map(str, sorted(data["responses"].keys())))
            avg_time = data.get("avg_time", 0)
            table.add_row(path, method, str(samples), statuses, f"{avg_time:.0f}")
    console.print(table)
