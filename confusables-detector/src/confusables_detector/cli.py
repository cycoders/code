import typer
from pathlib import Path
import sys
from typing import Optional

from rich.console import Console

from .scanner import scan_directory


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console(file=sys.stderr)


@app.command(help="Scan directory for confusables")
def scan(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False),
    exclude: str = typer.Option("", "--exclude", help="Comma-separated gitignore patterns"),
    json: bool = typer.Option(False, "--json", help="Output JSON stats"),
):
    """Scan for Unicode confusables."""
    excludes = [p.strip() for p in exclude.split(",") if p.strip()]

    try:
        stats = scan_directory(console, path, excludes, json)
        if json:
            print(stats, flush=True)
            raise typer.Exit(0 if stats["confusables"] == 0 else 1)
    except KeyboardInterrupt:
        console.print("\n⏹️  Interrupted.", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"💥 Error: {e}", style="red")
        raise typer.Exit(1)


def main():
    if __name__ == "__main__":
        app(prog_name="confusables-detector")
    else:
        app()
