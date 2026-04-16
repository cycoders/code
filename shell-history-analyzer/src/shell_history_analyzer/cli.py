import typer
from pathlib import Path
from typing import Optional

import rich

from . import __version__

from .parser import parse_history_file, detect_format
from .analyzer import analyze_history
from .suggester import suggest_optimizations
from .visualizer import print_analysis, print_suggestions, export_json

app = typer.Typer(no_args_is_help=True)
console = rich.Console()


@app.command()
def analyze(
    path: Path = typer.Argument(Path.home() / ".zsh_history", help="History file"),
    fmt: Optional[str] = typer.Option("auto", "--format", "auto|bash|zsh"),
    output: str = typer.Option("table", "--output", "table|json"),
    daily: bool = typer.Option(False, "--daily"),
):
    """Full analysis and visualization."""
    try:
        entries = parse_history_file(path, fmt)
        result = analyze_history(entries)
        if output == "table":
            print_analysis(result, daily)
        elif output == "json":
            export_json(result, Path("history-analysis.json"))
    except Exception as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1)


@app.command()
def suggest(
    path: Path = typer.Argument(Path.home() / ".zsh_history"),
    fmt: Optional[str] = typer.Option("auto"),
    min_repeats: int = typer.Option(10, "--min-repeats"),
    shell: str = typer.Option("zsh", "--shell", "zsh|bash"),
):
    """Suggest aliases and optimizations."""
    entries = parse_history_file(path, fmt)
    result = analyze_history(entries)
    sugs = suggest_optimizations(result)
    print_suggestions(sugs)


@app.command()
def stats(path: Path, fmt: Optional[str] = "auto"):
    """Quick stats only."""
    entries = parse_history_file(path, fmt)
    result = analyze_history(entries)
    typer.echo(f"Total: {result.total_commands:,} cmds | Top: {max(result.cmd_counter.values() or [0])}x")


@app.command()
def version():
    typer.echo(f"shistory v{__version__}")


if __name__ == "__main__":
    app()
