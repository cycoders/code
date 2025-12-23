import typer
from pathlib import Path
from .profiler import profile_imports
from .reporter import report_console, report_json, report_html

app = typer.Typer(help="Profile Python import startup times.")

@app.command()
def profile(
    script: Path = typer.Argument(..., exists=True, help="Python script to profile"),
    threshold_ms: float = typer.Option(1.0, "-t", "--threshold", help="Min ms to show (inclusive)"),
    output: Path = typer.Option(None, "-o", "--output", help="Export JSON/HTML"),
    tree: bool = typer.Option(True, "--tree/--no-tree"),
    table: bool = typer.Option(True, "--table/--no-table"),
    suggestions: bool = typer.Option(True, "--suggestions/--no-suggestions"),
):
    """Profile imports in SCRIPT during startup exec.

    Builds dep tree with incl/excl times.
    """
    try:
        data = profile_imports(str(script))
    except ValueError as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo("[yellow]Script errored post-imports; partial stats shown.[/yellow]")
        data = {}  # fallback empty

    if output:
        if output.suffix == ".json":
            report_json(data, str(output))
        elif output.suffix == ".html":
            report_html(data, threshold_ms, str(output))
        else:
            typer.echo("[red]Output must be .json or .html[/red]")
            raise typer.Exit(1)
    else:
        report_console(data, threshold_ms / 1000, tree, table, suggestions)

if __name__ == "__main__":
    app()
