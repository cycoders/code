import json
import sys
import typer
from pathlib import Path
from typing import List, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.group import Group

from .detector import detect_dupes

app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)

@app.command()
def cli(
    root: Path = typer.Argument(Path("."), help="Root directory to scan"),
    min_tokens: int = typer.Option(30, "--min-tokens", "-m", min=10, help="Minimum tokens per block"),
    threshold: float = typer.Option(0.85, "--threshold", "-t", min=0.0, max=1.0, help="Minimum similarity score"),
    step: int = typer.Option(5, "--step", min=1, help="Token step size for overlapping blocks"),
    max_results: int = typer.Option(20, "--max-results", "-n", min=1, help="Maximum dupes to report"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON instead of rich table"),
):
    """Detect duplicate code blocks in Python projects."""

    if not root.is_dir():
        typer.echo(f"Error: {root} is not a directory", err=True)
        raise typer.Exit(1)

    typer.echo(f"[bold green]Scanning {root} for duplicates...[/bold green]")

    try:
        dupes: List[Tuple[float, 'CodeBlock', 'CodeBlock']] = detect_dupes(
            root, min_tokens, threshold, step, max_results
        )
    except KeyboardInterrupt:
        typer.echo("\n[red]Scan interrupted.[/red]")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"[red]Error during scan: {e}[/red]")
        raise typer.Exit(1)

    if not dupes:
        typer.echo("[green]No duplicates found above threshold![/green]")
        raise typer.Exit(0)

    if json_output:
        data = [
            {
                "similarity": round(sim, 4),
                "block1": {
                    "path": b1.path,
                    "start_line": b1.start_line,
                    "end_line": b1.end_line,
                    "snippet": b1.snippet,
                },
                "block2": {
                    "path": b2.path,
                    "start_line": b2.start_line,
                    "end_line": b2.end_line,
                    "snippet": b2.snippet,
                },
            }
            for sim, b1, b2 in dupes
        ]
        print(json.dumps(data, indent=2))
        return

    typer.echo(f"[bold]Found {len(dupes)} duplicate(s) >= {threshold:.0%}:[/bold]")
    for sim, b1, b2 in dupes:
        title = f"{sim:.1%}  {b1.path}:{b1.start_line}-{b1.end_line}  ↔  {b2.path}:{b2.start_line}-{b2.end_line}"
        syntax1 = Syntax(b1.snippet.rstrip(), "python", line_numbers=True, word_wrap=False)
        syntax2 = Syntax(b2.snippet.rstrip(), "python", line_numbers=True, word_wrap=False)
        content = Group(syntax1, syntax2)
        panel = Panel(
            content,
            title=f"[bold white on blue]{title}[/bold white on blue]",
            box=box.ROUNDED,
            padding=(0, 1),
            expand=False,
        )
        console.print(panel)
        console.print()

if __name__ == "__main__":
    app()
