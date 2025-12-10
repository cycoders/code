import typer
from pathlib import Path
from typing import Annotated, List

import rich_click as rclick
from .core import diff_csvs
from .renderer import render_diff


app = typer.Typer(help="Precision CSV differ.", no_args_is_help=True)
rclick.rich_click.cli_style = "bright_blue"


@app.command()
def diff(
    file1: Path = typer.Argument(..., exists=True, help="Left CSV file"),
    file2: Path = typer.Argument(..., exists=True, help="Right CSV file"),
    keys: Annotated[
        List[str],
        typer.Option([], "-k", "--key", help="Key columns for matching (multi-ok)"),
    ] = [],
    ignore: Annotated[
        List[str],
        typer.Option([], "-i", "--ignore", help="Ignore these columns"),
    ] = [],
    tol: Annotated[
        float,
        typer.Option(0.0, "-t", "--tol", help="Numeric tolerance (e.g. 1e-6)"),
    ] = 0.0,
    output: Annotated[
        str, typer.Option("table", "-o", "--output", help="table|json")
    ] = "table",
):
    """
    Diff two CSV files semantically.
    """
    if output not in ("table", "json"):
        typer.echo("Error: output must be 'table' or 'json'", err=True)
        raise typer.Exit(1)

    result = diff_csvs(
        file1=str(file1),
        file2=str(file2),
        keys=keys,
        ignore=ignore,
        tol=tol,
    )
    render_diff(result, output)


if __name__ == "__main__":
    app()