import json
import sys
import typer
from typing import Annotated, Optional

from rich import print

from . import __version__
from .scanner import scan, SecretHit, Detection


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


def print_hits(hits: list[SecretHit], json_output: bool):
    if not hits:
        print("[bold green]No secrets detected! 🎉[/bold green]")
        raise typer.Exit(0)

    if json_output:
        print(json.dumps([h.__dict__ for h in hits], indent=2))
    else:
        from rich.table import Table
        from rich.console import Console

        console = Console()
        table = Table(title="Secrets Detected")
        table.add_column("Commit", style="cyan")
        table.add_column("File", style="magenta")
        table.add_column("Detector", style="yellow")
        table.add_column("Line", justify="right")
        table.add_column("Snippet", style="white")

        for hit in hits:
            commit_str = hit.commit or "working-tree"
            table.add_row(
                commit_str,
                hit.file_path,
                hit.detection.name,
                str(hit.detection.line),
                hit.detection.snippet,
            )
        console.print(table)
        print(f"[bold red]{len(hits)} secrets found. Review and remediate![/bold red]")

    raise typer.Exit(1)


@app.command()
def scan(
    path: str = ".",
    depth: Annotated[int, typer.Option(100, min=0, help="Max commits to scan (0=working tree only)" )] = 100,
    full_history: Annotated[bool, typer.Option(help="Scan full history (ignores depth, slow)" )] = False,
    exclude: Annotated[Optional[List[str]], typer.Option(help="Exclude globs (e.g. '.env*')" )] = None,
    allowlist: Annotated[Optional[List[str]], typer.Option(help="Ignore regex snippets" )] = None,
    patterns_file: Annotated[Optional[str], typer.Option(help="Custom patterns JSON" )] = None,
    entropy_thresh: Annotated[float, typer.Option(3.5, min=0.0, help="Entropy threshold (bits/char)" )] = 3.5,
    min_length: Annotated[int, typer.Option(20, min=5, help="Min length for entropy check" )] = 20,
    json: Annotated[bool, typer.Option(help="JSON output" )] = False,
):
    """Scan for secrets."""
    exclude_globs = exclude or []
    allowlist_re = allowlist or []

    try:
        hits = scan(
            path,
            depth,
            full_history,
            exclude_globs,
            patterns_file,
            entropy_thresh,
            min_length,
            allowlist_re,
        )
        print_hits(hits, json)
    except Exception as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1)


@app.command()
def patterns():
    """List built-in patterns."""
    from rich.table import Table

    table = Table(title="Detection Patterns")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Regex Preview")

    from .detectors import PATTERNS

    for pat in PATTERNS:
        regex_preview = pat["regex"][:50] + "..." if len(pat["regex"]) > 50 else pat["regex"]
        table.add_row(pat["id"], pat["name"], regex_preview)

    from rich.console import Console
    Console().print(table)


@app.command()
def version():
    """Show version."""
    print(f"git-secrets-scanner v{__version__}")


if __name__ == "__main__":
    app()