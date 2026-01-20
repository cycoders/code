import typer
from pathlib import Path
from typing_extensions import Annotated

import rich.console

from csv_profiler.profiler import profile_csv
from csv_profiler.renderers import render_table, render_json, render_html

app = typer.Typer(no_args_is_help=True)
console = rich.console.Console()

@app.command(help="Profile a CSV file")
def profile(
    path: Path = typer.Argument(..., exists=True, help="Path to CSV file"),
    max_rows: Annotated[int, typer.Option(100_000, "--max-rows", "-m", min=1, help="Max rows to scan")] = 100_000,
    output: Annotated[
        str,
        typer.Option("table", "--output", "-o", help="Output format")] = "table",
) -> None:
    """Generate comprehensive profile for CSV data."""
    try:
        data = profile_csv(path, max_rows)
        if output == "table" or output == "console":
            render_table(data)
        elif output == "json":
            console.print(render_json(data))
        elif output == "html":
            html = render_html(data)
            console.print(html, markup=False)
        else:
            raise typer.BadParameter(f"Unknown output: {output}")
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()