import typer
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .visitor import compute_complexity

app = typer.Typer()
console = Console()

@app.command()
def main(
    paths: List[Path] = typer.Argument([Path(".")], help="Paths (files/dirs) to analyze"),
    threshold: int = typer.Option(15, "--threshold/-t", min=1, help="Highlight functions >= this score"),
    fmt: str = typer.Option("table", "--format/-f", help="Output: table|json|csv"),
    output: Path = typer.Option(Path("-"), "--output/-o", help="Output file (-=stdout)"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
) -> None:
    """Compute cognitive complexity for Python code."""
    all_files: List[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            all_files.append(path)
        elif path.is_dir():
            all_files.extend(path.rglob("*.py"))

    if not all_files:
        typer.echo("No .py files found.", err=True)
        raise typer.Exit(1)

    all_metrics: List[Dict[str, Any]] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing Python files...", total=len(all_files))
        for file_path in all_files:
            metrics = compute_complexity(str(file_path))
            all_metrics.extend(metrics)
            progress.advance(task)

    high_complex = [m for m in all_metrics if m["complexity"] >= threshold]
    high_complex.sort(key=lambda m: m["complexity"], reverse=True)

    out_file = sys.stdout if output == "-" else open(output, "w", encoding="utf-8")

    if fmt == "table":
        table = Table(title=f"Cognitive Complexity >= {threshold}")
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Function", style="magenta")
        table.add_column("Line", justify="right")
        table.add_column("LOC", justify="right")
        table.add_column("Complexity", justify="right", style="red")
        for m in high_complex:
            rel_path = Path(m["file"]).relative_to(paths[0].parent if paths[0].is_file() else paths[0])
            table.add_row(str(rel_path), m["name"], str(m["lineno"]), str(m["loc"]), str(m["complexity"]))
        console.print(table)
        total_high = len(high_complex)
        console.print(f"\n[bold green]Total functions >= {threshold}: {total_high}[/bold green]")
        if total_high == 0:
            console.print("✅ All functions under threshold!")

    elif fmt == "json":
        data = {
            "all_metrics": all_metrics,
            "high_complexity": high_complex,
            "threshold": threshold,
            "summary": {
                "files_scanned": len(all_files),
                "total_functions": len(all_metrics),
                "max_complexity": max((m["complexity"] for m in all_metrics), default=0),
            }
        }
        json.dump(data, out_file, indent=2)

    elif fmt == "csv":
        if not high_complex:
            console.print("No high complexity functions.")
            return
        writer = csv.DictWriter(out_file, fieldnames=["file", "name", "lineno", "loc", "complexity"])
        writer.writeheader()
        writer.writerows(high_complex)
    else:
        typer.echo(f"Unknown format: {fmt}", err=True)
        raise typer.Exit(1)

    if output != "-":
        out_file.close()
        console.print(f"Output saved to [blue]{output}[/blue]")

if __name__ == "__main__":
    app()