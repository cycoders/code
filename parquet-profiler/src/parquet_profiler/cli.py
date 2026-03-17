import typer
from rich.traceback import install
install(show_locals=False)

from rich.console import Console

from .profiler import profile_dataset, get_schema, compare_datasets
from .types import OutputFormat

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()

@app.command(help="Full profile: schema, stats, quality, viz.")
def profile(
    path: str = typer.Argument(..., help="Path to Parquet file or directory"),
    columns: list[str] = typer.Option([], "--columns", help="Specific columns"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output"),
    limit_samples: int = typer.Option(1000, "--limit-samples"),
):
    """Profile Parquet dataset."""
    try:
        stats = profile_dataset(path, columns, limit_samples)
        if output == OutputFormat.JSON:
            console.print(stats.model_dump_json(indent=2))
        else:
            console.print(stats)  # Rich repr
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Schema inspection.")
def schema(
    path: str = typer.Argument(..., help="Path to Parquet file or directory"),
):
    """Inspect schema."""
    try:
        schema_info = get_schema(path)
        console.print(schema_info)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Compare two datasets.")
def compare(
    path1: str = typer.Argument(..., help="First Parquet"),
    path2: str = typer.Argument(..., help="Second Parquet"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output"),
):
    """Diff schema/stats between two Parquets."""
    try:
        diff = compare_datasets(path1, path2)
        if output == OutputFormat.JSON:
            console.print(diff.model_dump_json(indent=2))
        else:
            console.print(diff)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()

def main():
    app()
