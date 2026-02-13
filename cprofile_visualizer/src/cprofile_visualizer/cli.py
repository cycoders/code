import typer
from pathlib import Path
import sys

from rich.console import Console
from rich.traceback import install

from .runner import profile_run
from .parser import load_profile
from .visualizer import render_table, render_tree, render_flame
from .comparer import render_compare


install(show_locals=False)  # Graceful tracebacks

app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)  # Errors to stderr


@app.command()
def run(
    output: Path = typer.Option(Path("profile.prof"), "--output", "-o", exists=False),
    script_args: list[str] = typer.Argument(..., help="python myscript.py arg1 arg2"),
):
    """
    Profile a Python script with cProfile and save to .prof file.
    """
    if len(script_args) == 0:
        typer.echo("Error: Provide script path and args.", err=True)
        raise typer.Exit(1)

    script = script_args[0]
    args = script_args[1:]
    profile_run(script, output, args)
    typer.echo(f"✅ Profile saved: {output}")


@app.command()
def view(
    prof_file: Path = typer.Argument(..., exists=True, help=".prof file"),
    sort: str = typer.Option("cumtime", "--sort/-s", help="cumtime|tottime|calls|filename|name"),
    limit: int = typer.Option(50, "--limit/-l"),
    type_: str = typer.Option("table", "--type/-t", help="table|tree|flame"),
):
    """
    Visualize .prof file.
    """
    try:
        stats = load_profile(prof_file)
    except Exception as e:
        typer.echo(f"❌ Error loading {prof_file}: {e}", err=True)
        raise typer.Exit(1)

    render_type = type_.lower()
    if render_type == "table":
        render_table(stats, limit, console)
    elif render_type == "tree":
        render_tree(stats, limit, console)
    elif render_type == "flame":
        render_flame(stats, limit, console)
    else:
        typer.echo(f"❌ Unknown type: {type_} (table/tree/flame)", err=True)
        raise typer.Exit(1)


@app.command()
def compare(
    file1: Path = typer.Argument(..., exists=True),
    file2: Path = typer.Argument(..., exists=True),
    limit: int = typer.Option(30, "--limit/-l"),
    sort_by: str = typer.Option("delta", "--sort", help="delta|pct"),
):
    """
    Compare two .prof files (deltas, % change).
    """
    try:
        stats1 = load_profile(file1)
        stats2 = load_profile(file2)
    except Exception as e:
        typer.echo(f"❌ Load error: {e}", err=True)
        raise typer.Exit(1)

    render_compare(stats1, stats2, limit, console, sort_by)


if __name__ == "__main__":
    app(prog_name="cprof-viz")
